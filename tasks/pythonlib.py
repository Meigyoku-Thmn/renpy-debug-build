from renpybuild.model import task
import shutil

def copy_py_pyo(src, dst):
    """
    Copies the py, pyo and pem files from `src` to `dst`.

    `src` and `dst` may be either directories or files.
    """
    
    if src.is_dir():
        for i in src.iterdir():
            copy_py_pyo(i, dst / i.name)
        return

    if not (str(src).endswith(".py") or str(src).endswith(".pyo") or str(src).endswith(".pem")):
        return

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dst)


@task(kind="host-python", pythons="2", always=True)
def python2(c):
    
    c.clean("{{ distlib }}/{{ pythonver }}")                                                        # clean dst
    c.run("{{ hostpython }} -OO -m compileall {{ install }}/lib/{{ pythonver }}/site-packages")     # compile dependencies
    
    src_dir_path = c.path("{{ install }}/lib/{{ pythonver }}");
    dst_dir_path = c.path("{{ distlib }}/{{ pythonver }}");
    copy_py_pyo(src_dir_path, dst_dir_path)                                                            # copy the entire python lib
    
    src_dir_path = c.path("{{ pytmp }}/pyjnius/jnius");
    dst_dir_path = c.path("{{ distlib }}/{{ pythonver }}/jnius");
    copy_py_pyo(src_dir_path, dst_dir_path)                                                            # copy jnius
    
    src_dir_path = c.path("{{ pytmp }}/pyobjus/pyobjus");
    dst_dir_path = c.path("{{ distlib }}/{{ pythonver }}/pyobjus");
    copy_py_pyo(src_dir_path, dst_dir_path)                                                            # copy pyobjus
    
    c.run("mkdir -p {{ distlib }}/{{ pythonver }}/lib-dynload")
    with open(c.path("{{ distlib }}/{{ pythonver }}/lib-dynload/empty.txt"), "w") as f:
        f.write("lib-dynload needs to exist to stop an exec_prefix error.\n")
        
    c.copy("{{ install }}/lib/{{ pythonver }}/site.py", "{{ distlib }}/{{ pythonver }}/site.py")    # copy site.py
    
    customized_site_py_path = c.path("{{ runtime }}/site.py")                                       # append customized content to site.py
    with open(customized_site_py_path, "r") as customized_site_py_file:
        site_py_customized_content = customized_site_py_file.read()
    
    site_py_path = c.path("{{ distlib }}/{{ pythonver }}/site.py");    
    with open(site_py_path, "r") as site_py_file:
        site_py_content = site_py_file.read()
        
    site_py_content = site_py_content.replace("if hasattr(sys, \"setdefaultencoding\"):", "")
    site_py_content = site_py_content.replace("del sys.setdefaultencoding", "")
    site_py_customized_content = site_py_customized_content.replace(
        "sys.path = [ pythonlib + \"/site-packages\", pythonlib ]",
        "sys.path.append(pythonlib + \"/site-packages\")\n" +
        "sys.path.append(pythonlib)"
    )
    
    with open(site_py_path, "w") as site_py_file:
        site_py_file.write(site_py_content)
        site_py_file.write("\n")
        site_py_file.write(site_py_customized_content)
    
    c.run("{{ hostpython }} -OO -m compileall {{ distlib }}/{{ pythonver }}/site.py")               # compile the customized site.py
