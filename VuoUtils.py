import os
import platform

# Echoes and executes a shell command.
def system(command):
    print('        ' + command)
    os.system(command)

# Helper for fixLibs.
def fixIdAndRpath(library, deps_cpp_info):
    print('fixId(%s)' % library)
    if platform.system() == 'Darwin':
        system('install_name_tool -id @rpath/lib%s.dylib lib%s.dylib' % (library, library))
        if os.system('otool -l lib%s.dylib | grep LC_RPATH' % library) == 0:
            system('install_name_tool -rpath %s @loader_path lib%s.dylib' % (os.getcwd(), library))
        else:
            system('install_name_tool -add_rpath @loader_path lib%s.dylib' % library)
    elif platform.system() == 'Linux':
        patchelf = deps_cpp_info['patchelf'].rootpath + '/bin/patchelf'
        system('%s --set-soname lib%s.so lib%s.so' % (patchelf, library, library))
        system('%s --remove-rpath lib%s.so' % (patchelf, library))
    else:
        raise Exception('Unknown platform "%s"' % platform.system())

# Helper for fixLibs and fixExecutables.
def fixRefs(binary, librariesAndVersions, deps_cpp_info, dylibReferencesAreAbsolute):
    print('fixRefs(%s)' % binary)
    if platform.system() == 'Darwin':
        for lib, libVersion in librariesAndVersions.items():
            if dylibReferencesAreAbsolute:
                system('install_name_tool -change %s/lib%s.%s.dylib @rpath/lib%s.dylib %s' % (os.getcwd(), lib, libVersion, lib, binary))
            else:
                system('install_name_tool -change lib%s.dylib @rpath/lib%s.dylib %s' % (lib, lib, binary))
    elif platform.system() == 'Linux':
        patchelf = deps_cpp_info['patchelf'].rootpath + '/bin/patchelf'
        for lib, libVersion in librariesAndVersions.items():
            system('%s --replace-needed lib%s.so.%s lib%s.so %s' % (patchelf, lib, libVersion, lib, binary))
    else:
        raise Exception('Unknown platform "%s"' % platform.system())

# If dylibReferencesAreAbsolute is True,  each `LC_LOAD_DYLIB` command is expected to have the form `<current path>/libsomething.version.dylib` (typical).
# If dylibReferencesAreAbsolute is False, each `LC_LOAD_DYLIB` command is expected to have the form `libsomething.dylib` (no path or version, e.g., LLVM).
def fixLibs(librariesAndVersions, deps_cpp_info, dylibReferencesAreAbsolute=True):
    for lib in librariesAndVersions.keys():
        fixIdAndRpath(lib, deps_cpp_info)
        if platform.system() == 'Darwin':
            libraryFilename = 'lib%s.dylib' % lib
        elif platform.system() == 'Linux':
            libraryFilename = 'lib%s.so' % lib
        else:
            raise Exception('Unknown platform "%s"' % platform.system())
        fixRefs(libraryFilename, librariesAndVersions, deps_cpp_info, dylibReferencesAreAbsolute)

def fixExecutables(executables, librariesAndVersions, deps_cpp_info, dylibReferencesAreAbsolute=True):
    for executable in executables:
        fixRefs(executable, librariesAndVersions, deps_cpp_info, dylibReferencesAreAbsolute)
        if platform.system() == 'Darwin':
            system('install_name_tool -add_rpath @loader_path/../lib %s' % executable)
