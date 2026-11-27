#!/usr/bin/env python3
"""Trusted release controller for public IBERFIT Pages; no app or database access."""
import argparse, hashlib, json, os, re, subprocess, time, urllib.request, urllib.parse, zipfile
from pathlib import Path
from html.parser import HTMLParser
from xml.etree import ElementTree as ET

PROJECT = "web-iberfit"
ACCOUNT = "5b03d387427d367674b9d05b8bdf7c84"
PUBLIC = "https://iberfit.cl"
SHA = re.compile(r"[0-9a-f]{40}")
UUID = re.compile(r"[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}")
VERSION = re.compile(r"\d+\.\d+\.\d+(?:\.\d+)?")
def require(value, message):
    if not value:
        raise RuntimeError(message)

def request_data(path):
    data = json.loads(Path(path).read_text())
    common = {"schema", "mode", "source", "version", "previous_id"}
    prod = {"preview_id", "approval"}
    mode = data.get("mode")
    require(mode in ("preview", "production"), "Invalid mode")
    require(set(data) == common | (prod if mode == "production" else set()), "Unexpected request fields")
    require(data["schema"] == 1 and SHA.fullmatch(data["source"]) and VERSION.fullmatch(data["version"]) and UUID.fullmatch(data["previous_id"]), "Invalid release identity")
    if mode == "production":
        require(UUID.fullmatch(data["preview_id"]) and isinstance(data["approval"], str) and 8 <= len(data["approval"]) <= 300, "Missing explicit approval evidence")
    return data

def digest(data):
    return hashlib.sha256(data).hexdigest()

def unpack(package, manifest, dest, request):
    manifest = json.loads(Path(manifest).read_text())
    require(manifest["source"] == request["source"], "Package source mismatch")
    root = Path(dest)
    root.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(package) as z:
        names = z.namelist()
        require(len(names)==len(set(names)) and set(names)==set(manifest["files"]), "Package members mismatch")
        require(z.testzip() is None, "Corrupt ZIP")
        require(sum(i.file_size for i in z.infolist()) < 100_000_000, "Unexpected package size")
        for name in names:
            p = Path(name)
            require(not p.is_absolute() and ".." not in p.parts and "\\" not in name and not name.endswith("/"), "Unsafe package member")
            data = z.read(name)
            require(digest(data)==manifest["files"][name], "Package hash mismatch: "+name)
            target = root / p
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    require((root/"VERSION").read_text().strip()==request["version"], "Package version mismatch")
    require(all((root/x).is_file() for x in ("index.html","404.html","sitemap.xml","robots.txt")), "Missing web entrypoints")

def meta(d):
    return d.get("deployment_trigger", {}).get("metadata", {})

def verified(d, environment, source, branch=None):
    return d.get("environment")==environment and d.get("latest_stage", {}).get("status")=="success" and meta(d).get("commit_hash")==source and (branch is None or meta(d).get("branch")==branch)

def owned(d, source, previous, nonce):
    return d.get("id")!=previous and d.get("environment")=="production" and meta(d).get("commit_hash")==source and meta(d).get("commit_message")==nonce

def immutable_url(d, project=PROJECT):
    url = d.get("url","")
    require(re.fullmatch(r"https://[a-z0-9-]+\."+re.escape(project)+r"\.pages\.dev",url), "Unexpected deployment URL")
    return url

class Cloudflare:
    def __init__(self, token, project=PROJECT):
        self.project = project
        self.token = token
        self.base = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/pages/projects/{project}"
    def call(self, path="", method="GET"):
        req=urllib.request.Request(self.base+path, headers={"Authorization":"Bearer "+self.token}, method=method)
        with urllib.request.urlopen(req, timeout=30) as response:
            body=json.load(response)
        require(body.get("success") is True, "Cloudflare API failure: "+path)
        return body["result"]
    def project_state(self):
        r=self.call()
        require(r["name"]==self.project and r["production_branch"]=="production", "Unexpected project/branch")
        if self.project==PROJECT:
            require("iberfit.cl" in r["domains"], "Public domain missing")
        return r
    def active(self):
        return self.project_state()["canonical_deployment"]
    def deploy(self, directory, branch, source, nonce):
        subprocess.run([os.environ["WRANGLER_BIN"],"pages","deploy",str(directory),"--project-name",self.project,"--branch",branch,"--commit-hash",source,"--commit-message",nonce,"--commit-dirty=false"],check=True,timeout=300)
    def rollback(self, previous):
        self.call("/deployments/"+previous+"/rollback","POST")

class Canonical(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1=0
        self.canonical=[]
        self.lang=None
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=="h1": self.h1+=1
        if tag=="html": self.lang=a.get("lang")
        if tag=="link" and a.get("rel")=="canonical": self.canonical.append(a.get("href"))

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"IBERFIT-Release-QA/1","Cache-Control":"no-cache"})
    with urllib.request.urlopen(req,timeout=20) as r:
        require(r.status==200, "HTTP failure")
        return r.read()

def robots_match(actual, expected, exact):
    if actual==expected: return True
    if exact: return False
    # Cloudflare's managed robots overlay prepends a marked block on the
    # custom domain only. Preserve the complete operator policy verbatim.
    begin=b"# BEGIN Cloudflare Managed content"
    end=b"# END Cloudflare Managed Content"
    if actual.count(begin)!=1 or actual.count(end)!=1: return False
    prefix,suffix=actual.split(end,1)
    if begin not in prefix: return False
    preamble=prefix.split(begin,1)[0]
    if any(line.strip() and not line.lstrip().startswith(b"#") for line in preamble.splitlines()): return False
    return suffix.lstrip(b"\r\n")==expected

def smoke(base, root, version, exact=False):
    # Immutable deploys must match the certified bytes for key files; public
    # HTML may be transformed by Cloudflare (email protection, etc.).
    nonce="?release_check="+urllib.parse.quote(os.environ.get("GITHUB_RUN_ID","local"))
    require(get(base+"/VERSION"+nonce).decode().strip()==version, "Live version mismatch")
    urls=[x.text for x in ET.parse(root/"sitemap.xml").findall("{*}url/{*}loc")]
    require(len(urls)==len(set(urls)) and bool(urls), "Invalid sitemap")
    for url in urls:
        path=urllib.parse.urlsplit(url).path
        require(url==PUBLIC+path and path.startswith("/"), "Unexpected canonical")
        body=get(base+path+nonce)
        p=Canonical();p.feed(body.decode("utf-8"))
        require(p.h1==1 and p.canonical==[url] and p.lang==("en" if path.startswith("/en/") else "es"), "Live page semantics mismatch: "+path)
        if exact:
            require(body==(root/path.lstrip("/")/"index.html").read_bytes(), "Immutable HTML drift: "+path)
    for f in ("sitemap.xml","robots.txt","assets/styles.v628.css","assets/app.v628.js","assets/analytics.v628.js"):
        if (root/f).is_file():
            actual=get(base+"/"+f+nonce); expected=(root/f).read_bytes()
            require(robots_match(actual,expected,exact) if f=="robots.txt" else actual==expected, "Live asset drift: "+f)

def wait_for(fn, attempts=6, delay=5):
    last=None
    for i in range(attempts):
        try: return fn()
        except Exception as e:
            last=e
            if i+1<attempts: time.sleep(delay)
    raise RuntimeError("Verification failed") from last

def ready(url, version):
    # Newly created Pages hostnames can need TLS/edge propagation. Never disable TLS.
    wait_for(lambda: require(get(url+"/VERSION").decode().strip()==version,"Deployment not ready"),attempts=10,delay=8)

def promote(cf, request, directory, smoke_fn=smoke, public_origin=PUBLIC, nonce=None):
    nonce = nonce or ("iberfit-release-"+os.environ["GITHUB_RUN_ID"]+"-"+os.environ.get("GITHUB_RUN_ATTEMPT","1"))
    require(re.fullmatch(r"iberfit-release-[a-zA-Z0-9-]{1,100}", nonce), "Invalid release attempt identity")
    previous=request["previous_id"]
    source=request["source"]
    version=request["version"]
    before=cf.active()
    require(before["id"]==previous and before["environment"]=="production" and before["latest_stage"]["status"]=="success","Production base changed or unhealthy")
    # A rollback target must exist and be a successful production deployment.
    old=cf.call("/deployments/"+previous)
    require(old["id"]==previous and old["environment"]=="production" and old["latest_stage"]["status"]=="success","Rollback target unavailable")
    old_version=get(public_origin+"/VERSION").decode().strip()
    require(VERSION.fullmatch(old_version), "Invalid public baseline")
    if request["mode"]=="preview":
        branch="review-"+source[:12]
        cf.deploy(directory,branch,source,nonce)
        def find():
            ds=cf.call("/deployments?env=preview")
            valid=[d for d in ds if verified(d,"preview",source,branch) and meta(d).get("commit_message")==nonce]
            require(bool(valid), "No certified preview")
            return valid[0]
        d=wait_for(find)
        ready(immutable_url(d,cf.project),version)
        smoke_fn(immutable_url(d,cf.project),directory,version,True)
        require(cf.active()["id"]==previous,"Production changed concurrently")
        return d
    p=cf.call("/deployments/"+request["preview_id"])
    require(p["id"]==request["preview_id"] and verified(p,"preview",source,"review-"+source[:12]),"Preview does not match approved source")
    ready(immutable_url(p,cf.project),version)
    smoke_fn(immutable_url(p,cf.project),directory,version,True)
    require(cf.active()["id"]==previous,"Production changed during preflight")
    try:
        cf.deploy(directory,"production",source,nonce)
        def deployed():
            d=cf.active()
            require(owned(d,source,previous,nonce) and verified(d,"production",source,"production"), "Production identity mismatch")
            return d
        d=wait_for(deployed)
        ready(immutable_url(d,cf.project),version)
        smoke_fn(immutable_url(d,cf.project),directory,version,True)
        wait_for(lambda:smoke_fn(public_origin,directory,version,False),attempts=4,delay=10)
        require(cf.active()["id"]==d["id"],"Production changed during validation")
        return d
    except Exception:
        recover_owned(cf,source,previous,nonce,old_version,public_origin)
        raise

def recover_owned(cf,source,previous,nonce,old_version,public_origin):
    # Never revert another release; fail closed on ambiguous state.
    active=cf.active()
    if owned(active,source,previous,nonce):
        cf.rollback(previous)
        def restored():
            require(cf.active()["id"]==previous,"Rollback deployment not active")
            require(get(public_origin+"/VERSION").decode().strip()==old_version,"Rollback public version mismatch")
        wait_for(restored)
        print("ROLLBACK_CONFIRMED="+previous)
        return True
    if active["id"]==previous:
        print("PRODUCTION_UNCHANGED")
    else:
        print("MANUAL_RECOVERY_REQUIRED: unrelated deployment active")
    return False

def main():
    a=argparse.ArgumentParser()
    a.add_argument("manifest")
    a.add_argument("--package")
    a.add_argument("--hashes")
    a.add_argument("--dest")
    a.add_argument("--validate-only",action="store_true")
    args=a.parse_args()
    request=request_data(args.manifest)
    if args.validate_only:
        print(json.dumps(request))
        return
    require(os.environ.get("CLOUDFLARE_API_TOKEN"),"Missing Cloudflare token")
    unpack(args.package,args.hashes,args.dest,request)
    d=promote(Cloudflare(os.environ["CLOUDFLARE_API_TOKEN"]),request,Path(args.dest))
    evidence={"mode":request["mode"],"source":request["source"],"version":request["version"],"deployment_id":d["id"],"url":immutable_url(d),"previous_id":request["previous_id"]}
    Path("pages-release-evidence.json").write_text(json.dumps(evidence,indent=2)+"\n")
    print(json.dumps(evidence))
if __name__=="__main__":
    main()
