import os
from scripts.paths import list_dir


def listdir(self, root):
    allowed = list_dir()
    list_dir_allowed = []
    list_dir_root = os.listdir(root)
    for i in list_dir_root:
        path = os.path.join(root, i).replace('\\', '/')
        for j in allowed:
            if path in j:
                list_dir_allowed.append(i)
                break
            else:
                if os.path.isfile(path):
                    if root.replace('\\', '/') == j:
                        list_dir_allowed.append(i)
                        break
    return list_dir_allowed


def get_root():
    allowlist = list_dir()
    roots = []

    def appdend_root(index=1):
        for i in allowlist:
            root = '/'.join(i.split('/')[:index]) + '/'
            if root not in roots:
                roots.append(root)
        return roots
    appdend_root()
    appdend_root(2)
    return roots
