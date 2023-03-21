#include "histogram.hpp"

#include <vector>
#include <limits>

Histogram::Histogram(const std::vector<double>& data, std::size_t num_bins)
    : bin_size(1.0), data_size(data.size())
{
    double max = std::numeric_limits<double>::lowest();
    for (const auto& v : data)
    {
        if (v < 0.0) return;
        if (max < v) max = v;
    }

    counts.resize(num_bins, 0);
    bin_size = max / num_bins;

    for (const auto& v : data)
    {
        counts[std::min((std::size_t)(v / bin_size), num_bins - 1)]++;
    }
}

double Histogram::level(double count_percentage) const
{
    auto num = static_cast<std::size_t>(data_size * count_percentage);
    std::size_t count = 0;
    double level = 0.0;
    for (std::size_t i = 0; i < counts.size(); i++)
    {
        count += counts[i];
        if (count >= num)
        {
            level = (i + 1) * bin_size;
            break;
        }
    }
    return level;
}
