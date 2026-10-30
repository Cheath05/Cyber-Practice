CXX      ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -Wpedantic

carver: carver.cpp
	$(CXX) $(CXXFLAGS) -o $@ $<

# Build a test image with 3 JPEGs hidden in random bytes, then carve it
test: carver
	python3 make_test_image.py test.raw
	./carver test.raw carved_out

clean:
	rm -rf carver test.raw carved_out

.PHONY: test clean
