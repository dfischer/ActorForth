//
//	stack.cpp	- Stack implementation for ActorForth.
//

#include <doctest/doctest.h>

#include <iostream>
#include <variant>
#include <utility>

#include "stack.hpp"


template<class T> const std::vector<T> Stack<T>::AlwaysEmpty;

StackSig StackSig::make_stacksig(const Type& type)  
{
	return StackSig( std::make_pair(type, std::make_optional<AnyValue>()) );
}

std::ostream& operator<<(std::ostream& out, const StackObject& obj)
{
	out << "<StackObject>{" << obj.first << ", val: ";
	//out << obj.second;
	out << "VALUE?";

	out << "}";
	return out;
}

std::ostream& operator<<(std::ostream& out, const StackSig& sig) 
{ 
	out << "<StackSig>{" << sig.first << ", ";
	if(sig.second.has_value())
	{
		out << "filter val:";
		//out << sig.second.value();
		out << "VALUE?";
	}
	else
	{
		out << "<no filter>";
	}
	out << "}"; 
	return out; 
}

std::ostream& operator<<(std::ostream& out, const Signature& sig)
{
	out << "<Signature>{in=";

	auto v = std::get_if<Stack<StackSig>::NonEmpty>(&(sig.in_seq._stack));
	if(not v)
	{
		out << "<empty>} out=";
	}
	else
	{
		std::for_each(v->_data.begin(), v->_data.end(), [&out](const StackSig& s) { out << s << ","; } );
		out << "} out=";	
	}

	v = std::get_if<Stack<StackSig>::NonEmpty>(&(sig.out_seq._stack));
	if(not v)
	{
		out << "<empty>}";
	}
	else
	{
		std::for_each(v->_data.begin(), v->_data.end(), [&out](const StackSig& s) { out << s << ","; } );
		out << "}";	
	}

	return out;
}


bool StackSig::operator==(const StackSig& s) const
{
	// Generic Types always match.
	if(first.id == 0) return true;

	// Different Types fail.
	if(first.id != s.first.id) return false;

	// If both our signatures specifies a value check it as well.
	if(second.has_value() and s.second.has_value() and second.value() != s.second.value()) return false;

	return true;
}


bool StackSig::operator==(const StackObject& o) const
{
	// Generic Types always match.
	if(first.id == 0) return true;

	// Different Types fail.
	if(first.id != o.first.id) return false;

	// If our signature specifies a value check it as well.
	if(second.has_value() and second.value() != o.second) return false;

	return true;
}


// Confirms whether or not the inbound stack complies with this Signature.
// Only the last n stack entries are checked where n = in_seq.depth().
bool Signature::matches(const Stack<StackObject>& sobjects) const
{
	// If our input signature is empty then it's a match!
	if(in_seq.depth() == 0) return true;

	// Is sobject long enough?
	if(sobjects.depth() < in_seq.depth()) return false;
	
	auto o = sobjects.rbegin();
	for(auto s = in_seq.rbegin(); s != in_seq.rend();++s)
	{
		if(*s != *o++) return false;
	}

	return true;
}
	

bool Signature::matches(const Stack<StackSig>& sig) const
{
	// If our input signature is empty then it's a match!
	if(in_seq.depth() == 0) return true;

	// Is sobject long enough?
	if(sig.depth() < in_seq.depth()) return false;
	
	auto o = sig.rbegin();
	for(auto s = in_seq.rbegin(); s != in_seq.rend();++s)
	{
		if(*s != *o++) return false;
	}

	return true;
}
