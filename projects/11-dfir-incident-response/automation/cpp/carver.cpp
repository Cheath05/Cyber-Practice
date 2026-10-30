// carver.cpp - carve JPEG files out of a raw disk image by signature (Project 11 C++ exercise).
//
// Deleted files usually remain on disk until overwritten. Carvers ignore the filesystem and
// scan raw bytes for known headers/footers. JPEG: header FF D8 FF, footer FF D9.
//
// Build: make            Run: ./carver image.raw out_dir [max_size_bytes]
// Simplification: a real carver also validates JPEG segment structure; this one carves from
// each header to the first footer after it, capped at max_size.
#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <string>
#include <vector>

namespace fs = std::filesystem;

int main(int argc, char **argv) {
    if (argc < 3) {
        std::cerr << "usage: " << argv[0] << " <image> <out_dir> [max_size_bytes]\n";
        return 1;
    }
    const std::string image = argv[1];
    const fs::path out_dir = argv[2];
    const std::size_t max_size = argc > 3 ? std::strtoull(argv[3], nullptr, 10) : 20u * 1024 * 1024;

    std::ifstream in(image, std::ios::binary);
    if (!in) { std::cerr << "cannot open " << image << "\n"; return 1; }
    // Small lab images fit in memory; a production carver would stream in chunks.
    std::vector<std::uint8_t> data((std::istreambuf_iterator<char>(in)), std::istreambuf_iterator<char>());
    fs::create_directories(out_dir);

    const std::uint8_t header[] = {0xFF, 0xD8, 0xFF};
    const std::uint8_t footer[] = {0xFF, 0xD9};
    std::size_t found = 0;
    auto pos = data.begin();
    while (true) {
        auto start = std::search(pos, data.end(), std::begin(header), std::end(header));
        if (start == data.end()) break;
        auto limit = (static_cast<std::size_t>(data.end() - start) > max_size) ? start + max_size : data.end();
        auto end = std::search(start + 3, limit, std::begin(footer), std::end(footer));
        if (end == limit) { pos = start + 1; continue; }   // no footer in range: not a complete JPEG
        end += 2;                                           // include the footer bytes
        const auto offset = static_cast<std::size_t>(start - data.begin());
        const fs::path out = out_dir / ("carved_" + std::to_string(found) + "_off" + std::to_string(offset) + ".jpg");
        std::ofstream(out, std::ios::binary).write(reinterpret_cast<const char *>(&*start), end - start);
        std::cout << "carved " << out.string() << " (" << (end - start) << " bytes at offset " << offset << ")\n";
        ++found;
        pos = end;
    }
    std::cout << found << " JPEG(s) carved\n";
    return found ? 0 : 2;
}
