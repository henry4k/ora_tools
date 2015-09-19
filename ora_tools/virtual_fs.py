import zipfile
import posixpath
import os.path

def check_mode(vfs_mode, file_mode):
    if vfs_mode == 'r':
        if file_mode != 'r':
            raise RuntimeError('Mode ot allowed.')

class VirtualFileSystem:
    def __init__(self, mode):
        self.mode = mode

    def open(self, filename, mode):
        pass

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

class ZipFileSystem(VirtualFileSystem):
    def __init__(self, file_path, mode):
        VirtualFileSystem.__init__(self, mode)
        self.zip_file = zipfile.ZipFile(file_path, mode)

    def open(self, file_path, mode):
        check_mode(self.mode, mode)
        if mode == 'r':
            return self.zip_file.open(file_path, 'r')
        else:
            pass # TODO

    def close(self):
        self.zip_file.close()

class DirectoryFileSystem(VirtualFileSystem):
    def __init__(self, file_path, mode):
        VirtualFileSystem.__init__(self, mode)
        self.file_path = file_path
        if mode == 'w':
            if os.path.isdir(file_path):
                os.removedirs(file_path)
                os.mkdir(file_path)
        if mode == 'a':
            if os.path.isdir(file_path):
                os.mkdir(file_path)

    def open(self, file_path, mode):
        check_mode(self.mode, mode)
        real_path = os.path.join(self.file_path, file_path)
        return open(real_path, mode)
