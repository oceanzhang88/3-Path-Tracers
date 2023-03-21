#include "linear-octree.hpp"

#include <algorithm>

#include <glm/gtx/norm.hpp>

#include "../common/constexpr-math.hpp"
#include "../common/util.hpp"

template <class Data>
LinearOctree<Data>::LinearOctree(Octree<Data> &octree_root)
{
    size_t octree_size = 0, data_size = 0;
    octreeSize(octree_root, octree_size, data_size);

    if (octree_size == 0 || data_size == 0) return;

    uint32_t df_idx = ROOT_IDX;
    uint64_t data_idx = 0;
    uint64_t contained_data;
    compact(&octree_root, df_idx, data_idx, contained_data, true);
}

template <class Data>
void LinearOctree<Data>::knnSearch(const glm::dvec3& p, size_t k, PriorityQueue<SearchResult<Data>>& result) const
{
    result.clear();

    if (linear_tree.empty()) return;

    if (k > ordered_data.size()) k = ordered_data.size();

    double max_distance2 = std::numeric_limits<double>::max();

    auto updateMaxDistance = [&](double d2) { if (d2 < max_distance2) max_distance2 = d2; };

    struct alignas(16) DNode
    {
        bool operator< (const DNode& rhs) const { return rhs.distance2 < distance2; };
        double distance2;
        uint32_t octant;
    };

    thread_local PriorityQueue<DNode> to_visit; to_visit.clear();

    DNode current{ linear_tree[ROOT_IDX].BB.distance2(p), ROOT_IDX };

    while (true)
    {
        const auto& node = linear_tree[current.octant];
        if (node.leaf || node.contained_data <= k)
        {
            uint64_t end_idx = node.start_data + node.contained_data;
            for (uint64_t i = node.start_data; i < end_idx; i++)
            {
                const auto& data = ordered_data[i];
                double distance2 = glm::distance2(data.pos(), p);
                if (distance2 <= max_distance2)
                {
                    if (result.size() < k - 1)
                    {
                        // Insert the first k elements without maintaining the heap-property.
                        result.push_unordered({ data, distance2 });
                    }
                    else
                    {
                        if (result.size() != k)
                        {
                            result.push_unordered({ data, distance2 });
                            // Create valid heap now that k elements have been found.
                            result.make_heap();
                        }
                        else
                        {
                            // Pop the farthest of the k elements and push the closer new element.
                            result.pop_push({ data, distance2 });
                        }
                        // No k-NN element can be farther than the farthest element in the current set of k elements.
                        updateMaxDistance(result.top().distance2);
                    }
                }
            }
        }
        else
        {
            uint32_t child_octant = current.octant + 1;
            while (child_octant != NULL_IDX)
            {
                const auto& child_node = linear_tree[child_octant];

                double distance2 = child_node.BB.distance2(p);
                if (distance2 <= max_distance2)
                {
                    to_visit.push({ distance2, child_octant });

                    if (child_node.contained_data >= k)
                    {
                        // No k-NN element can be farther than the farthest corner in a node that contains k elements.
                        updateMaxDistance(child_node.BB.max_distance2(p));
                    }
                }
                child_octant = child_node.next_sibling;
            }
        }

        if (to_visit.empty())
        {
            break;
        }
        else
        {
            current = to_visit.top();
            if (current.distance2 > max_distance2) break;
            to_visit.pop();
        }
    }
}

template <class Data>
void LinearOctree<Data>::octreeSize(const Octree<Data> &octree_root, size_t &size, size_t &data_size) const
{
    if (octree_root.leaf() && octree_root.data_vec.empty()) return;

    size++;
    data_size += octree_root.data_vec.size();

    if (!octree_root.leaf())
    {
        for (const auto &octant : octree_root.octants)
        {
            octreeSize(*octant, size, data_size);
        }
    }
}

template <class Data>
BoundingBox LinearOctree<Data>::compact(Octree<Data>* node, uint32_t& df_idx, uint64_t& data_idx, uint64_t& contained_data, bool last)
{
    uint32_t idx = df_idx++;

    linear_tree.emplace_back();
    linear_tree[idx].leaf = (uint8_t)node->leaf();
    linear_tree[idx].start_data = data_idx;
    linear_tree[idx].contained_data = node->data_vec.size();

    BoundingBox BB;
    if (!node->data_vec.empty())
    {
        for (auto&& data : node->data_vec) BB.merge(data.pos());
        ordered_data.insert(ordered_data.end(), node->data_vec.begin(), node->data_vec.end());
        data_idx += node->data_vec.size();
        node->data_vec.clear();
        node->data_vec.shrink_to_fit();
    }

    if (!node->leaf())
    {
        std::vector<size_t> use;
        for (size_t i = 0; i < node->octants.size(); i++)
        {
            if (!(node->octants[i]->leaf() && node->octants[i]->data_vec.empty()))
            {
                use.push_back(i);
            }
        }
        for (const auto& i : use)
        {
            uint64_t child_data;
            BB.merge(compact(node->octants[i].get(), df_idx, data_idx, child_data, i == use.back()));
            linear_tree[idx].contained_data += child_data;
        }
    }
    node->octants.clear();
    node->octants.shrink_to_fit();
    linear_tree[idx].next_sibling = last ? NULL_IDX : df_idx;
    linear_tree[idx].BB = BB;
    contained_data = linear_tree[idx].contained_data;
    return BB;
}
