#pragma once

#include <string>
#include <filesystem>
#include <utility>
#include <vector>

struct Option
{
    Option(std::filesystem::path  path, std::string  camera, int camera_idx, bool photon_map)
        : path(std::move(path)), camera(std::move(camera)), camera_idx(camera_idx), photon_map(photon_map){ }

    std::filesystem::path path;
    std::string camera;
    int camera_idx;
    bool photon_map;
};

std::vector<Option> availible(const std::filesystem::path& path);

Option getOption(std::vector<Option>& options);
