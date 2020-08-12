%include std_string.i
%include std_vector.i

// Instantiations of templates of some standard vectors
namespace std {
   %template(SCharVector)      vector<signed char>;
   %template(UCharVector)      vector<unsigned char>;
   %template(ShortVector)      vector<short>;
   %template(UShortVector)     vector<unsigned short>;
   %template(LongVector)       vector<long>;
   %template(ULongVector)      vector<unsigned long>;
   %template(IntVector)        vector<int>;
   %template(LLongVector)      vector<long long>;
   %template(UIntVector)       vector<unsigned>;
   %template(ULLongVector)     vector<unsigned long long>;
   %template(FloatVector)      vector<float>;
   %template(DoubleVector)     vector<double>;
   %template(LDoubleVector)    vector<long double>;
   %template(StringVector)     vector<std::string>;
}
