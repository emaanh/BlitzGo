#include <iostream>
#include <vector>
#include <set>
#include <unordered_map>
#include <ctime>
#include <cstdlib>
#include <deque>
#include <stdexcept>
#include <cmath>
#include <cstring>
#include <algorithm>
#include <numeric>

class Board {
public:
    static const int WALL_NORTH = 1 << 0;  // Bit 0
    static const int WALL_SOUTH = 1 << 1;  // Bit 1
    static const int WALL_WEST = 1 << 2;   // Bit 2
    static const int WALL_EAST = 1 << 3;   // Bit 3
    static const int LOOK_UP_MASK = 61440;

    Board(int size) : size(size), size_2(size * size), total_territory_count(0), current_hash(0), intermediateHash(0) {
        stones.resize(size, std::vector<void*>(size, nullptr));
        territory.resize(size, std::vector<void*>(size, nullptr));
        control_map.resize(size, std::vector<int>(size, 0));
        vector_gravity_map.resize(size, std::vector<std::vector<int>>(size, std::vector<int>(2, 0)));
        tension_map.resize(size, std::vector<int>(size, 0));
        zobrist_table.resize(size, std::vector<std::vector<long long>>(size, std::vector<long long>(3, 0)));
        initialize_zobrist_hash(size);
    }

    std::vector<std::vector<int>> create_heuristic_maps() {
        std::vector<std::vector<std::vector<int>>> heuristic_maps(15, std::vector<std::vector<int>>(size, std::vector<int>(size, 0)));

        for (int exclude_walls = 0; exclude_walls < 15; ++exclude_walls) {
            std::vector<std::vector<int>> distances;

            if (!(exclude_walls & WALL_NORTH)) {
                std::vector<int> north(size);
                std::iota(north.begin(), north.end(), 0);
                distances.push_back(north);
            }
            if (!(exclude_walls & WALL_SOUTH)) {
                std::vector<int> south(size);
                std::iota(south.begin(), south.end(), 0);
                std::transform(south.begin(), south.end(), south.begin(), [this](int val) { return size - 1 - val; });
                distances.push_back(south);
            }
            if (!(exclude_walls & WALL_WEST)) {
                std::vector<int> west(size);
                std::iota(west.begin(), west.end(), 0);
                distances.push_back(west);
            }
            if (!(exclude_walls & WALL_EAST)) {
                std::vector<int> east(size);
                std::iota(east.begin(), east.end(), 0);
                std::transform(east.begin(), east.end(), east.begin(), [this](int val) { return size - 1 - val; });
                distances.push_back(east);
            }

            for (auto& d : distances) {
                for (int i = 0; i < size; ++i) {
                    for (int j = 0; j < size; ++j) {
                        heuristic_maps[exclude_walls][i][j] = std::min(heuristic_maps[exclude_walls][i][j], d[i]);
                    }
                }
            }
        }

        return heuristic_maps;
    }

    int playerNumberID(void* player) {
        for (size_t i = 0; i < players.size(); ++i) {
            if (players[i] == player) {
                return i;
            }
        }
        return -1;
    }

    int player_to_state(void* player) {
        if (player == nullptr) {
            return 0;
        } else if (player == players[0]) {
            return 1;
        } else if (player == players[1]) {
            return 2;
        } else {
            throw std::invalid_argument("Unknown player identifier");
        }
    }

    void initialize_zobrist_hash(int size) {
        for (int y = 0; y < size; ++y) {
            for (int x = 0; x < size; ++x) {
                for (int state = 1; state < 3; ++state) {  // Only generate numbers for player1 and player2
                    zobrist_table[y][x][state] = rand() % (1ULL << 64);
                }
            }
        }
    }

    void update_hash(std::pair<int, int> position, void* old_player, void* new_player) {
        int x = position.first, y = position.second;

        int old_state = player_to_state(old_player);
        int new_state = player_to_state(new_player);
        if (old_state != 0) {
            current_hash ^= zobrist_table[y][x][old_state];
        }
        if (new_state != 0) {
            current_hash ^= zobrist_table[y][x][new_state];
        }
    }

    bool isValidMove(std::pair<int, int> position) {
        int x = position.first, y = position.second;
        return is_within_bounds(position) && stones[y][x] == nullptr;
    }

    bool isDuplicateMove() {
        if (board_set.find(current_hash) != board_set.end()) {
            return true;
        } else {
            intermediateHash = current_hash;
            return false;
        }
    }

    void removeStone(std::pair<int, int> position) {
        int x = position.first, y = position.second;
        update_hash(position, stones[y][x], nullptr);
        update_board_change(stones[y][x], position, -1);
        stones[y][x] = nullptr;
    }

    bool is_within_bounds(std::pair<int, int> position) {
        int x = position.first, y = position.second;
        return 0 <= x && x < size && 0 <= y && y < size;
    }

    bool remove_last_move(std::pair<int, int> position) {
        int x = position.first, y = position.second;
        if (stones[y][x] != nullptr && territory[y][x] != nullptr && stones[y][x] != territory[y][x]) {
            update_board_change(territory[y][x], position, 1);
            removeStone(position);
            return true;
        }
        return false;
    }

    int placeStone(void* player, std::pair<int, int> position) {
        clock_t start_time2 = clock();

        int x = position.first, y = position.second;

        if (!isValidMove(position)) {
            return 1;  // for invalid move
        }

        stones[y][x] = player;
        update_hash(position, nullptr, player);

        if (isDuplicateMove()) {
            removeStone(position);
            incrementTerritory(player, 1);  // Adjusting for duplicate check
            return 2;  // for duplicate move
        }

        update_board_change(player, position, 1);
        bool captured = update_other_stones(player, position);
        move_history.push_back(position);

        return 0;  // for successful move
    }

    bool double_suicide(void* player, std::pair<int, int> position) {
        if (move_history.empty()) {
            return false;
        }
        int x = position.first, y = position.second;
        auto [x_prev, y_prev] = move_history.back();
        return territory[y][x] != player && territory[y][x] != nullptr && territory[y_prev][x_prev] == player;
    }

    bool update_other_stones(void* player, std::pair<int, int> position) {
        bool captured = update_territories_and_remove_inside_stones(player, position);
        bool penetrated = false;

        if (captured) {
            penetrated = bfs_update_opponent_territory(player, position);
        }

        if (penetrated || double_suicide(player, position)) {
            board_set.insert(intermediateHash);
        }

        if (!move_history.empty()) {
            if (remove_last_move(move_history.back())) {
                captured = true;
            }
        }
        removeSingleTerritory(position);
        return captured;
    }

    void removeSingleTerritory(std::pair<int, int> position) {
        int x = position.first, y = position.second;
        if (territory[y][x] != nullptr && stones[y][x] != nullptr && territory[y][x] != stones[y][x]) {
            update_board_change(territory[y][x], position, -1);
        }
    }

    bool update_territories_and_remove_inside_stones(void* player, std::pair<int, int> position) {
        int x = position.first, y = position.second;
        std::set<std::pair<int, int>> total_territory;
        bool captured = false;

        if (territory[y][x] == player) {
            update_board_change(player, position, -1);
            territory[y][x] = nullptr;
            return captured;
        }

        std::set<std::pair<int, int>> totalVisited;
        std::vector<std::pair<int, int>> directions = { {0, 1}, {1, 0}, {0, -1}, {-1, 0} };
        for (auto [dx, dy] : directions) {
            int nx = position.first + dx, ny = position.second + dy;
            if (is_within_bounds({nx, ny}) && stones[ny][nx] != player && totalVisited.find({nx, ny}) == totalVisited.end()) {
                auto enclosed_territory = dfs_enclosed_territory(player, {nx, ny}, totalVisited);
                if (!enclosed_territory.empty()) {
                    for (auto [tx, ty] : enclosed_territory) {
                        if (territory[ty][tx] != player) {
                            if (territory[ty][tx] != nullptr) {
                                update_board_change(territory[ty][tx], {tx, ty}, -1);
                            }
                            update_board_change(player, {tx, ty}, 1);
                            territory[ty][tx] = player;
                        }
                        if (stones[ty][tx] != nullptr && stones[ty][tx] != player) {
                            removeStone({tx, ty});
                            captured = true;
                        }
                    }
                }
            }
        }

        return captured;
    }

    bool bfs_update_opponent_territory(void* player, std::pair<int, int> start) {
        bool anyUpdated = false;
        std::deque<std::pair<int, int>> queue = { start };
        int x = start.first, y = start.second;

        if (is_within_bounds({x, y}) && territory[y][x] != player && territory[y][x] != nullptr) {
            update_board_change(territory[y][x], {x, y}, -1);
            territory[y][x] = nullptr;
            anyUpdated = true;
        }

        while (!queue.empty()) {
            auto [x, y] = queue.front();
            queue.pop_front();
            for (auto [dx, dy] : directions) {
                int nx = x + dx, ny = y + dy;

                if (is_within_bounds({nx, ny}) && territory[ny][nx] != player && territory[ny][nx] != nullptr) {
                    queue.push_back({nx, ny});
                    update_board_change(territory[ny][nx], {nx, ny}, -1);
                    territory[ny][nx] = nullptr;
                    anyUpdated = true;
                }
            }
        }

        return anyUpdated;
    }

    std::set<std::pair<int, int>> dfs_enclosed_territory(void* player, std::pair<int, int> start, std::set<std::pair<int, int>>& totalVisited) {
        std::deque<std::pair<int, int>> queue = { start };
        totalVisited.insert(start);
        std::set<std::pair<int, int>> visited = { start };
        int walls_touched = 0;

        while (!queue.empty()) {
            auto [x, y] = queue.back();
            queue.pop_back();

            for (auto [dx, dy] : directions) {
                int nx = x + dx, ny = y + dy;

                if (visited.find({nx, ny}) != visited.end()) {
                    continue;
                }

                if (ny < 0) {
                    walls_touched |= WALL_NORTH;
                } else if (ny >= size) {
                    walls_touched |= WALL_SOUTH;
                } else if (nx < 0) {
                    walls_touched |= WALL_WEST;
                } else if (nx >= size) {
                    walls_touched |= WALL_EAST;
                } else {
                    if (stones[ny][nx] != player) {
                        queue.push_back({nx, ny});
                        totalVisited.insert({nx, ny});
                        visited.insert({nx, ny});
                    }
                }
            }
            if (LOOK_UP_MASK & (1 << walls_touched)) {
                return {};
            }
        }

        return visited;
    }

    bool stability_test(std::pair<int, int> position) {
        int x = position.first, y = position.second;
        void* player = territory[y][x];

        if (player == nullptr) {
            throw std::runtime_error("Win check called when board wasn't filled.");
        }

        int countCorner = 0;

        for (auto [dx, dy] : directions) {
            int nx = x + dx, ny = y + dy;
            if (is_within_bounds({nx, ny}) && stones[ny][nx] != nullptr && stones[ny][nx] != player) {
                countCorner++;
            }
        }

        if (countCorner >= 2) {
            return false;
        }

        if (countCorner == 1) {
            if (x == 0 || y == 0 || x == size - 1 || y == size - 1) {
                return false;
            }
        }

        return true;
    }

    bool checkGameOver() {
        for (int y = 0; y < size; ++y) {
            for (int x = 0; x < size; ++x) {
                if (territory[y][x] != nullptr && !stability_test({x, y})) {
                    return false;
                }
            }
        }
        return true;
    }

    void initalizeTerritoryCounts(void* player) {
        territory_counts[player] = 0;
    }

    int totalTerritory() {
        return total_territory_count;
    }

    void incrementTerritory(void* player, int delta) {
        territory_counts[player] += delta;
        total_territory_count += delta;
    }

    void printBothTerritories() {
        for (const auto& player : territory_counts) {
            std::cout << player.first << "'s territory: " << player.second << std::endl;
        }
        std::cout << "Total: " << total_territory_count << std::endl;
    }

private:
    int size;
    int size_2;
    int total_territory_count;
    long long current_hash;
    long long intermediateHash;
    std::vector<std::vector<void*>> stones;
    std::vector<std::vector<void*>> territory;
    std::vector<void*> players;
    std::unordered_map<void*, int> territory_counts;
    std::set<long long> board_set;
    std::vector<std::vector<std::vector<long long>>> zobrist_table;
    std::vector<std::vector<int>> control_map;
    std::vector<std::vector<std::vector<int>>> vector_gravity_map;
    std::vector<std::vector<int>> tension_map;
    std::vector<std::vector<std::vector<int>>> heuristic_maps;
    std::vector<std::pair<int, int>> move_history;
    std::vector<std::pair<int, int>> directions = { {0, 1}, {1, 0}, {0, -1}, {-1, 0} };

    void update_board_change(void* player, std::pair<int, int> position, int delta) {
        // Implementation of board change logic
    }
};

