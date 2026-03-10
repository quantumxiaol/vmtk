set(vtkAddon_version "cf1126568415179fb5b1c16121087bd2494e2e0e")

set(vtkMacroKitPythonWrap.cmake_expected_hash "1b6ce9c4a8d5aaad253797d7ce66d31270cb647e3641a69f3d585c9a08341668")
set(vtkWrapHierarchy.cmake_expected_hash "c9343c54675e8bbde8ceaedf99a3226546b5f7d4cf7d5dac3e33db9093b536f2")
set(vtkWrapPython.cmake_expected_hash "ac22023ff10c58da33c2a6633fc90fde9863f12bb0f90dd0da51e18796137db3")
set(vtkWrapperInit.data.in_expected_hash "3e840679603eb4a0d425c1244828729cb271f33a081c5ac2e0547aa747bbec5d")
option(VMTK_ALLOW_CMAKE_DOWNLOADS "Allow downloading helper CMake files at configure time." OFF)

foreach(filename IN ITEMS
  vtkMacroKitPythonWrap.cmake
  vtkWrapHierarchy.cmake
  vtkWrapPython.cmake
  vtkWrapperInit.data.in
  )
  set(dest_file "${CMAKE_CURRENT_BINARY_DIR}/${filename}")
  set(expected_hash "${${filename}_expected_hash}")
  set(url "https://raw.githubusercontent.com/Slicer/vtkAddon/${vtkAddon_version}/CMake/${filename}")

  # Prefer local vendored copies to avoid network dependency during configure.
  set(local_source "")
  foreach(candidate IN ITEMS
    "${CMAKE_CURRENT_SOURCE_DIR}/${filename}"
    "${CMAKE_CURRENT_LIST_DIR}/${filename}"
    "${CMAKE_CURRENT_LIST_DIR}/../vtkVmtk/Wrapping/${filename}"
    )
    if(EXISTS "${candidate}")
      set(local_source "${candidate}")
      break()
    endif()
  endforeach()

  if(local_source)
    file(SHA256 "${local_source}" local_hash)
    if(NOT "${local_hash}" STREQUAL "${expected_hash}")
      message(WARNING "Using local ${filename} with SHA256=${local_hash} "
        "(expected ${expected_hash}).")
    endif()
    configure_file("${local_source}" "${dest_file}" COPYONLY)
    continue()
  endif()

  if(EXISTS "${dest_file}")
    file(SHA256 "${dest_file}" current_hash)
    if(NOT "${current_hash}" STREQUAL "${expected_hash}")
      if(VMTK_ALLOW_CMAKE_DOWNLOADS)
        file(DOWNLOAD "${url}" "${dest_file}" EXPECTED_HASH SHA256="${expected_hash}")
      else()
        message(FATAL_ERROR
          "Cached ${filename} hash mismatch at ${dest_file}. "
          "Set VMTK_ALLOW_CMAKE_DOWNLOADS=ON to refresh from ${url}.")
      endif()
    endif()
  else()
    if(VMTK_ALLOW_CMAKE_DOWNLOADS)
      file(DOWNLOAD "${url}" "${dest_file}" EXPECTED_HASH SHA256="${expected_hash}")
    else()
      message(FATAL_ERROR
        "Missing required helper file ${filename}. Expected local copy under ${CMAKE_CURRENT_SOURCE_DIR} "
        "or set VMTK_ALLOW_CMAKE_DOWNLOADS=ON.")
    endif()
  endif()
endforeach()

set(vtkAddon_CMAKE_DIR ${CMAKE_CURRENT_BINARY_DIR} CACHE PATH "Path to vtkAddon CMake directory")
