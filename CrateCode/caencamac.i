%module caencamac

%{
#define SWIG_FILE_WITH_INIT
%}
%include "numpy.i"
%init %{
import_array();
%}

// std_sstream.i must be included before std_string.i (due to a bug in SWIG)
%include std_sstream.i
%include stdint.i
%include stddecls.i
%include exception.i

%exception {
  try {
    $action
  } catch (const std::exception& e) {
    SWIG_exception(SWIG_RuntimeError, e.what());
  }
}

%include "crate_lib_defs.i"
%include "CrateHandle.i"
