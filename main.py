from __future__ import annotations
from typing import List
from typing_extensions import Never

def assert_never(arg: Never) -> Never:
    raise AssertionError("Expected code to be unreachable")

class INode:
  def __init__(self, name: str):
    self.name = name
  def __repr__(self):
    return self.name

class File(INode): pass

class Link(INode):
  def __init__(self, alias: str, dest: INode):
    super().__init__(alias)
    self.dest = dest

class Repo(INode):
  def __init__(self, name: str, dirs: List[Repo] = [], files: List[File] = [], parent: INode = None):
    super().__init__(name)
    # insert child nodes
    self.children = dict()
    for x in files: self.insert(x)
    for x in dirs: self.insert(x)
    # wiring
    self.children["."] = self
    if parent is not None: self.children[".."] = parent
  
  def list(self):
    return list(self.children.keys())
  
  def insert(self, node: INode): 
    self.children[node.name] = node
    if isinstance(node, Repo):
      node.children[".."] = self # wiring back
  
  def removeByName(self, victim): del self.children[victim]

class App:
  def __init__(self, root_fs: Repo):
    self.root = root_fs
    self.pwd = self.root

  def ls(self):
    print(self.pwd.list())
  
  def cd(self, destname):
    child = self.pwd.children[destname]
    if isinstance(child, Link):
      self.pwd = child.dest
    elif isinstance(child, Repo):
      self.pwd = child
    else:
      assert_never("invalid args for 'cd'")

  def mkdir(self, dirname):
    self.pwd.insert(Repo(dirname))
  
  def rm(self, dirname):
    self.pwd.removeByName(dirname)
  
  def dir(self): return self.pwd.name
  
  def touch(self, filename):
    self.pwd.insert(File(filename))


def execute(app: App, command):
  [command, *args] = str(command).split(" ")
  match command:
    case "ls": app.ls()
    case "cd": app.cd(args[0])
    case "mkdir": app.mkdir(args[0])
    case "rmdir": app.rm(args[0])
    case "touch": app.touch(args[0])
    case "rm": app.rm(args[0])
    case "": pass
    case c_: print("Invalid command", c_)


def main():
  app = App(root_fs=Repo("/emul/"))

  def test_on_production():
    commands = ["ls", "mkdir dir1", "mkdir dir2", "cd dir2", "touch file1", "touch file2", "cd .", "cd ..", "touch file0", "touch never", "rm never", "ls"]
    for c in commands: execute(app, c)
  test_on_production()

  while True:
    command = input("phuc@PHUC:{dir}$ ".format(dir=app.dir()))
    if command == 'exit': break
    execute(app, command)

main()