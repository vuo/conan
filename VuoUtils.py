import os
import platform

def system(command):
    """
    Echoes and executes a shell command.
    """
    print('        ' + command)
    os.system(command)

def fixIdAndRpath(library, deps_cpp_info):
    """
    Helper for fixLibs.
    Modifies `library`:
       - Changes its dylib self-identification to use `@rpath`
       - Removes its absolute search path (if any)
       - Adds `@loader_path` search path (if it doesn't already have that one)
    @todo update Linux
    """
    print('fixId(%s)' % library)
    if platform.system() == 'Darwin':
        system('install_name_tool -id @rpath/lib%s.dylib lib%s.dylib' % (library, library))
        if os.system('otool -l lib%s.dylib | fgrep -A2 LC_RPATH | fgrep %s' % (library, os.getcwd())) == 0:
            system('install_name_tool -delete_rpath %s lib%s.dylib' % (os.getcwd(), library))
        if os.system('otool -l lib%s.dylib | fgrep -A2 LC_RPATH | fgrep @loader_path' % library) != 0:
            system('install_name_tool -add_rpath @loader_path lib%s.dylib' % library)
    elif platform.system() == 'Linux':
        patchelf = deps_cpp_info['patchelf'].rootpath + '/bin/patchelf'
        system('%s --set-soname lib%s.so lib%s.so' % (patchelf, library, library))
        system('%s --remove-rpath lib%s.so' % (patchelf, library))
    else:
        raise Exception('Unknown platform "%s"' % platform.system())

def fixRefs(binary, librariesAndVersions, deps_cpp_info):
    """
    Helper for fixLibs and fixExecutables.
    Modifies `binary`, normalizing its references to other dylibs:
       - Changes absolute paths to `librariesAndVersions` (if any) to `@rpath` references
       - Changes `@rpath` references to `librariesAndVersions` that include the version number (if any) to `@rpath` references without the version number
    @todo update Linux
    """
    print('fixRefs(%s)' % binary)
    if platform.system() == 'Darwin':
        for lib, libVersion in librariesAndVersions.items():
            absoluteLoadPath = '%s/lib%s.%s.dylib' % (os.getcwd(), lib, libVersion)
            rpathVersionLoadPath = '@rpath/lib%s.%s.dylib' % (lib, libVersion)
            if os.system('otool -L %s | fgrep "%s"' % (binary, absoluteLoadPath)) == 0:
                system('install_name_tool -change %s @rpath/lib%s.dylib %s' % (absoluteLoadPath, lib, binary))
            elif os.system('otool -L %s | fgrep "%s"' % (binary, rpathVersionLoadPath)) == 0:
                system('install_name_tool -change %s @rpath/lib%s.dylib %s' % (rpathVersionLoadPath, lib, binary))
    elif platform.system() == 'Linux':
        patchelf = deps_cpp_info['patchelf'].rootpath + '/bin/patchelf'
        for lib, libVersion in librariesAndVersions.items():
            system('%s --replace-needed lib%s.so.%s lib%s.so %s' % (patchelf, lib, libVersion, lib, binary))
    else:
        raise Exception('Unknown platform "%s"' % platform.system())

def fixLibs(librariesAndVersions, deps_cpp_info):
    for lib in librariesAndVersions.keys():
        fixIdAndRpath(lib, deps_cpp_info)
        if platform.system() == 'Darwin':
            libraryFilename = 'lib%s.dylib' % lib
        elif platform.system() == 'Linux':
            libraryFilename = 'lib%s.so' % lib
        else:
            raise Exception('Unknown platform "%s"' % platform.system())
        fixRefs(libraryFilename, librariesAndVersions, deps_cpp_info)

def fixExecutables(executables, librariesAndVersions, deps_cpp_info):
    for executable in executables:
        fixRefs(executable, librariesAndVersions, deps_cpp_info)
        if platform.system() == 'Darwin':
            system('install_name_tool -add_rpath @loader_path/../lib %s' % executable)
