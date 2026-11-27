#!/usr/bin/env python3
"""Isolated fault-injection tests: no network or Cloudflare credentials."""
import importlib.util, json, tempfile, unittest, zipfile
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location("release",Path(__file__).with_name("pages_release_360.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
S="a"*40
NONCE="iberfit-release-test-1"
OLD="11111111-1111-1111-1111-111111111111"
NEW="22222222-2222-2222-2222-222222222222"
PRE="33333333-3333-3333-3333-333333333333"
OTHER="44444444-4444-4444-4444-444444444444"
def dep(id, env="production", source=S, branch="production", nonce=NONCE):
    return {"id":id,"environment":env,"latest_stage":{"status":"success"},"url":"https://abcdef.web-iberfit.pages.dev","deployment_trigger":{"metadata":{"commit_hash":source,"branch":branch,"commit_message":nonce}}}
def req(mode="production"):
    d={"schema":1,"mode":mode,"source":S,"version":"6.43.32","previous_id":OLD}
    if mode=="production":d.update(preview_id=PRE,approval="Reviewed and approved")
    return d
class Fake:
    project=m.PROJECT
    def __init__(self):
        self.old=dep(OLD,source="b"*40);self.current=self.old
        self.preview=dep(PRE,"preview",branch="review-"+S[:12])
        self.rollbacks=[];self.deployments=[]
        self.fail=False;self.unrelated=False
    def active(self):return self.current
    def call(self,path):
        if path.startswith("/deployments?"):return [self.preview]
        return {"/deployments/"+OLD:self.old,"/deployments/"+PRE:self.preview}[path]
    def deploy(self,directory,branch,source,nonce):
        self.deployments.append(branch)
        if branch=="production":
            self.current=dep(OTHER,source="c"*40) if self.unrelated else dep(NEW,nonce=nonce)
        if self.fail:raise RuntimeError("injected deployment failure")
    def rollback(self,id):
        self.rollbacks.append(id);self.current=self.old
class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.cf=Fake()
        self.mock=patch.object(m,"get",side_effect=lambda url:b"6.43.31" if url.startswith(m.PUBLIC) else b"6.43.32")
        self.mock.start();self.addCleanup(self.mock.stop)
        self.wait=patch.object(m.time,"sleep");self.wait.start();self.addCleanup(self.wait.stop)
    def run_release(self,request=None,smoke=None):
        return m.promote(self.cf,request or req(),Path("."),smoke or (lambda *a:None),nonce=NONCE)
    def test_preview_no_production_mutation(self):
        self.assertEqual(self.run_release(req("preview"))["id"],PRE)
        self.assertEqual(self.cf.deployments,["review-"+S[:12]])
        self.assertEqual(self.cf.active()["id"],OLD)
    def test_production_success(self):
        self.assertEqual(self.run_release()["id"],NEW)
        self.assertEqual(self.cf.rollbacks,[])
    def test_changed_base_stops(self):
        self.cf.current=dep(OTHER)
        with self.assertRaises(RuntimeError):self.run_release()
        self.assertEqual(self.cf.deployments,[])
    def test_wrong_preview_stops(self):
        self.cf.preview=dep(PRE,"preview",source="d"*40,branch="review-"+S[:12])
        with self.assertRaises(RuntimeError):self.run_release()
        self.assertEqual(self.cf.deployments,[])
    def test_failed_preview_smoke_stops(self):
        def bad(*a):raise RuntimeError("bad preview")
        with self.assertRaises(RuntimeError):self.run_release(smoke=bad)
        self.assertEqual(self.cf.deployments,[])
    def test_failed_public_smoke_rolls_back_owned_release(self):
        def smoke(base,*a):
            if base==m.PUBLIC:raise RuntimeError("public unhealthy")
        with self.assertRaises(RuntimeError):self.run_release(smoke=smoke)
        self.assertEqual(self.cf.rollbacks,[OLD]);self.assertEqual(self.cf.active()["id"],OLD)
    def test_deploy_failure_after_activation_rolls_back(self):
        self.cf.fail=True
        with self.assertRaises(RuntimeError):self.run_release()
        self.assertEqual(self.cf.rollbacks,[OLD])
    def test_unrelated_concurrent_release_never_rolled_back(self):
        self.cf.unrelated=True
        with self.assertRaises(RuntimeError):self.run_release()
        self.assertEqual(self.cf.rollbacks,[])
        self.assertEqual(self.cf.active()["id"],OTHER)
    def test_same_sha_different_attempt_never_rolled_back(self):
        def external(*args):self.cf.current=dep(OTHER,nonce="iberfit-release-other-1")
        self.cf.deploy=external
        with self.assertRaises(RuntimeError):self.run_release()
        self.assertEqual(self.cf.rollbacks,[])
    def test_rollback_target_unavailable(self):
        self.cf.old["latest_stage"]["status"]="failure"
        with self.assertRaises(RuntimeError):self.run_release()
        self.assertEqual(self.cf.deployments,[])
    def test_no_approval_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"request.json";r=req();r.pop("approval");p.write_text(json.dumps(r))
            with self.assertRaises(RuntimeError):m.request_data(p)
    def test_manifest_injection_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"request.json";r=req();r["source"]="a; echo unsafe";p.write_text(json.dumps(r))
            with self.assertRaises(RuntimeError):m.request_data(p)
    def test_package_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as t:
            t=Path(t);p=t/"package.zip";h=t/"hashes.json"
            with zipfile.ZipFile(p,"w") as z:z.writestr("VERSION",b"6.43.32")
            h.write_text(json.dumps({"source":S,"files":{"VERSION":"0"*64}}))
            with self.assertRaises(RuntimeError):m.unpack(p,h,t/"out",req())
    def test_package_path_traversal(self):
        with tempfile.TemporaryDirectory() as t:
            t=Path(t);p=t/"package.zip";h=t/"hashes.json"
            with zipfile.ZipFile(p,"w") as z:z.writestr("../escape",b"bad")
            h.write_text(json.dumps({"source":S,"files":{"../escape":m.digest(b"bad")}}))
            with self.assertRaises(RuntimeError):m.unpack(p,h,t/"out",req())
            self.assertFalse((t/"escape").exists())
    def test_managed_robots_prefix_only_on_public(self):
        expected=b"User-agent: OAI-SearchBot\nAllow: /\n"
        actual=b"# managed explanation\n# BEGIN Cloudflare Managed content\nUser-agent: GPTBot\nDisallow: /\n# END Cloudflare Managed Content\n"+expected
        self.assertTrue(m.robots_match(actual,expected,False))
        self.assertFalse(m.robots_match(actual,expected,True))
        self.assertFalse(m.robots_match(actual+b"Disallow: /\n",expected,False))
        self.assertFalse(m.robots_match(b"User-agent: *\nDisallow: /\n"+actual,expected,False))
    def test_valid_package(self):
        with tempfile.TemporaryDirectory() as t:
            t=Path(t);p=t/"package.zip";h=t/"hashes.json"
            files={"VERSION":b"6.43.32","index.html":b"index","404.html":b"404","sitemap.xml":b"xml","robots.txt":b"robots"}
            with zipfile.ZipFile(p,"w") as z:
                for n,b in files.items():z.writestr(n,b)
            h.write_text(json.dumps({"source":S,"files":{n:m.digest(b) for n,b in files.items()}}))
            m.unpack(p,h,t/"out",req())
            self.assertEqual((t/"out"/"VERSION").read_bytes(),files["VERSION"])
if __name__=="__main__":unittest.main(verbosity=2)
