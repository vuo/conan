import os
import platform

def fixId(library, deps_cpp_info):
    if platform.system() == 'Darwin':
        os.system('install_name_tool -id @rpath/lib%s.dylib lib%s.dylib' % (library, library))
        os.system('install_name_tool -rpath %s @loader_path lib%s.dylib' % (os.getcwd(), library))
    elif platform.system() == 'Linux':
        patchelf = deps_cpp_info['patchelf'].rootpath + '/bin/patchelf'
        os.system('%s --set-soname lib%s.so lib%s.so' % (patchelf, library, library))
        os.system('%s --remove-rpath lib%s.so' % (patchelf, library))
    else:
        raise Exception('Unknown platform "%s"' % platform.system())

def fixRefs(library, librariesAndVersions, deps_cpp_info):
    if platform.system() == 'Darwin':
        for lib, libVersion in librariesAndVersions.items():
            os.system('install_name_tool -change %s/lib%s.%s.dylib @rpath/lib%s.dylib lib%s.dylib' % (os.getcwd(), lib, libVersion, lib, library))
    elif platform.system() == 'Linux':
        patchelf = deps_cpp_info['patchelf'].rootpath + '/bin/patchelf'
        for lib, libVersion in librariesAndVersions.items():
            os.system('%s --replace-needed lib%s.so.%s lib%s.so lib%s.so' % (patchelf, lib, libVersion, lib, library))
    else:
        raise Exception('Unknown platform "%s"' % platform.system())

def fixLibs(librariesAndVersions, deps_cpp_info):
    for lib in librariesAndVersions.keys():
        fixId(lib, deps_cpp_info)
        fixRefs(lib, librariesAndVersions, deps_cpp_info)
