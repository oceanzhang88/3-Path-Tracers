#pragma once

#include <vector>

class Histogram
{
public:
    Histogram(const std::vector<double>& data, std::size_t num_bins);

    [[nodiscard]] double level(double count_percentage) const;

    std::vector<std::size_t> counts;
    double bin_size;
    std::size_t data_size;
};
