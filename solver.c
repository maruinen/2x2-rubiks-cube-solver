#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

/* --- Color Enumerations and Mappings --- */
typedef enum {
    W = 0, Y = 1, R = 2, O = 3, B = 4, G = 5, UNKNOWN = 6
} Color;

const char int_to_char_color[] = {'W', 'Y', 'R', 'O', 'B', 'G'};

Color char_to_int_color(char c) {
    switch (c) {
        case 'W': return W;
        case 'Y': return Y;
        case 'R': return R;
        case 'O': return O;
        case 'B': return B;
        case 'G': return G;
        default: return UNKNOWN;
    }
}

/* --- Cube State Representation --- */
#define NUM_STICKERS 24

typedef struct {
    uint8_t stickers[NUM_STICKERS];
} CubeState;

/* Solved state */
const char* SOLVED_STATE_STR = 
    "WWWW"  /* U-face (White)  */
    "GGGG"  /* F-face (Green)  */
    "RRRR"  /* R-face (Red)    */
    "BBBB"  /* B-face (Blue)   */
    "OOOO"  /* L-face (Orange) */
    "YYYY"; /* D-face (Yellow) */

CubeState SOLVED_STATE;

/* --- BFS Node Structure --- */
typedef struct {
    CubeState state;
    int parent_idx;
    const char* move_from_parent;
} BFSNode;

/* --- Visited State Tracking (using simple array-based hash set) --- */
#define VISITED_TABLE_SIZE 1000000
typedef struct {
    CubeState state;
    bool occupied;
} VisitedEntry;

VisitedEntry visited_table[VISITED_TABLE_SIZE];

/* Hash function for cube state */
static uint32_t hash_state(const CubeState* state) {
    uint32_t hash = 5381;
    for (int i = 0; i < NUM_STICKERS; i++) {
        hash = ((hash << 5) + hash) ^ state->stickers[i];
    }
    return hash % VISITED_TABLE_SIZE;
}

/* Check if state was visited, and mark as visited if not */
static bool mark_visited(const CubeState* state) {
    uint32_t idx = hash_state(state);
    uint32_t probe = 0;
    
    while (probe < VISITED_TABLE_SIZE) {
        uint32_t pos = (idx + probe) % VISITED_TABLE_SIZE;
        
        if (!visited_table[pos].occupied) {
            /* Found empty slot, mark as visited */
            visited_table[pos].state = *state;
            visited_table[pos].occupied = true;
            return true;
        }
        
        if (memcmp(visited_table[pos].state.stickers, state->stickers, NUM_STICKERS) == 0) {
            /* Already visited */
            return false;
        }
        
        probe++;
    }
    
    /* Table is full */
    return false;
}

/* --- Cube Manipulation Functions --- */

static void copy_state(CubeState* dest, const CubeState* src) {
    memcpy(dest->stickers, src->stickers, NUM_STICKERS);
}

static bool is_solved(const CubeState* cube) {
    return memcmp(cube->stickers, SOLVED_STATE.stickers, NUM_STICKERS) == 0;
}

static void rotate_face_cw(CubeState* cube, int start) {
    uint8_t temp = cube->stickers[start];
    cube->stickers[start] = cube->stickers[start + 2];
    cube->stickers[start + 2] = cube->stickers[start + 3];
    cube->stickers[start + 3] = cube->stickers[start + 1];
    cube->stickers[start + 1] = temp;
}

/* Apply a single clockwise face rotation (R, U, or F) */
static void apply_single_move(CubeState* cube, char face) {
    CubeState original;
    copy_state(&original, cube);
    
    if (face == 'R') {
        /* Rotate R face */
        rotate_face_cw(cube, 8);
        
        /* Cycle edges: U(right) -> B(left) -> D(right) -> F(right) -> U(right) */
        cube->stickers[1]  = original.stickers[15]; /* U1 <- B3 */
        cube->stickers[3]  = original.stickers[13]; /* U3 <- B1 */
        cube->stickers[5]  = original.stickers[1];  /* F1 <- U1 */
        cube->stickers[7]  = original.stickers[3];  /* F3 <- U3 */
        cube->stickers[21] = original.stickers[5];  /* D1 <- F1 */
        cube->stickers[23] = original.stickers[7];  /* D3 <- F3 */
        cube->stickers[15] = original.stickers[21]; /* B3 <- D1 */
        cube->stickers[13] = original.stickers[23]; /* B1 <- D3 */
        
    } else if (face == 'U') {
        /* Rotate U face */
        rotate_face_cw(cube, 0);
        
        /* Cycle edges: F -> L -> B -> R -> F */
        cube->stickers[4]  = original.stickers[8];  /* F0 <- R0 */
        cube->stickers[5]  = original.stickers[9];  /* F1 <- R1 */
        cube->stickers[8]  = original.stickers[12]; /* R0 <- B0 */
        cube->stickers[9]  = original.stickers[13]; /* R1 <- B1 */
        cube->stickers[12] = original.stickers[16]; /* B0 <- L0 */
        cube->stickers[13] = original.stickers[17]; /* B1 <- L1 */
        cube->stickers[16] = original.stickers[4];  /* L0 <- F0 */
        cube->stickers[17] = original.stickers[5];  /* L1 <- F1 */
        
    } else if (face == 'F') {
        /* Rotate F face */
        rotate_face_cw(cube, 4);
        
        /* Cycle edges: U(bottom) -> R(left) -> D(top) -> L(right) -> U(bottom) */
          /* NOTE: ensure these form two separate 4-cycles (U2->R0->D0->L1 and U3->R2->D1->L3)
              Previously this used L3/L1 which created an 8-cycle and made the inverse
              move incorrect. Use L1 for U2 and L3 for U3. */
          cube->stickers[2]  = original.stickers[17]; /* U2 <- L1 */
          cube->stickers[3]  = original.stickers[19]; /* U3 <- L3 */
        cube->stickers[8]  = original.stickers[2];  /* R0 <- U2 */
        cube->stickers[10] = original.stickers[3];  /* R2 <- U3 */
        cube->stickers[20] = original.stickers[8];  /* D0 <- R0 */
        cube->stickers[21] = original.stickers[10]; /* D1 <- R2 */
        cube->stickers[17] = original.stickers[20]; /* L1 <- D0 */
        cube->stickers[19] = original.stickers[21]; /* L3 <- D1 */
    }
}

/* Apply a move (can be R, R', R2, U, U', U2, F, F', F2) */
static CubeState apply_move(const CubeState* state, const char* move) {
    CubeState result;
    copy_state(&result, state);
    
    char face = move[0];
    int count = 1;
    
    if (strlen(move) == 2) {
        if (move[1] == '\'') {
            count = 3; /* Prime = 3 clockwise rotations */
        } else if (move[1] == '2') {
            count = 2; /* Double move */
        }
    }
    
    for (int i = 0; i < count; i++) {
        apply_single_move(&result, face);
    }
    
    return result;
}

/* --- Parse Input File --- */
static void parse_input_file(const char* filename, CubeState* cube) {
    FILE* fp = fopen(filename, "r");
    if (!fp) {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }
    
    char line[256];
    
    /* Read U face (2 lines) */
    fgets(line, sizeof(line), fp);
    cube->stickers[0] = char_to_int_color(line[0]);
    cube->stickers[1] = char_to_int_color(line[1]);
    
    fgets(line, sizeof(line), fp);
    cube->stickers[2] = char_to_int_color(line[0]);
    cube->stickers[3] = char_to_int_color(line[1]);
    
    /* Read L-F-R-B faces (2 lines) */
    fgets(line, sizeof(line), fp);
    cube->stickers[16] = char_to_int_color(line[0]); /* L0 */
    cube->stickers[17] = char_to_int_color(line[1]); /* L1 */
    cube->stickers[4]  = char_to_int_color(line[2]); /* F0 */
    cube->stickers[5]  = char_to_int_color(line[3]); /* F1 */
    cube->stickers[8]  = char_to_int_color(line[4]); /* R0 */
    cube->stickers[9]  = char_to_int_color(line[5]); /* R1 */
    cube->stickers[12] = char_to_int_color(line[6]); /* B0 */
    cube->stickers[13] = char_to_int_color(line[7]); /* B1 */
    
    fgets(line, sizeof(line), fp);
    cube->stickers[18] = char_to_int_color(line[0]); /* L2 */
    cube->stickers[19] = char_to_int_color(line[1]); /* L3 */
    cube->stickers[6]  = char_to_int_color(line[2]); /* F2 */
    cube->stickers[7]  = char_to_int_color(line[3]); /* F3 */
    cube->stickers[10] = char_to_int_color(line[4]); /* R2 */
    cube->stickers[11] = char_to_int_color(line[5]); /* R3 */
    cube->stickers[14] = char_to_int_color(line[6]); /* B2 */
    cube->stickers[15] = char_to_int_color(line[7]); /* B3 */
    
    /* Read D face (2 lines) */
    fgets(line, sizeof(line), fp);
    cube->stickers[20] = char_to_int_color(line[0]);
    cube->stickers[21] = char_to_int_color(line[1]);
    
    fgets(line, sizeof(line), fp);
    cube->stickers[22] = char_to_int_color(line[0]);
    cube->stickers[23] = char_to_int_color(line[1]);
    
    fclose(fp);
}

/* --- Print Cube State --- */
static void print_state(const CubeState* cube) {
    printf("U-Face:\n");
    printf("%c%c\n", int_to_char_color[cube->stickers[0]], int_to_char_color[cube->stickers[1]]);
    printf("%c%c\n", int_to_char_color[cube->stickers[2]], int_to_char_color[cube->stickers[3]]);
    
    printf("L-F-R-B Faces:\n");
    printf("%c%c%c%c%c%c%c%c\n",
           int_to_char_color[cube->stickers[16]], int_to_char_color[cube->stickers[17]],
           int_to_char_color[cube->stickers[4]],  int_to_char_color[cube->stickers[5]],
           int_to_char_color[cube->stickers[8]],  int_to_char_color[cube->stickers[9]],
           int_to_char_color[cube->stickers[12]], int_to_char_color[cube->stickers[13]]);
    printf("%c%c%c%c%c%c%c%c\n",
           int_to_char_color[cube->stickers[18]], int_to_char_color[cube->stickers[19]],
           int_to_char_color[cube->stickers[6]],  int_to_char_color[cube->stickers[7]],
           int_to_char_color[cube->stickers[10]], int_to_char_color[cube->stickers[11]],
           int_to_char_color[cube->stickers[14]], int_to_char_color[cube->stickers[15]]);
    
    printf("D-Face:\n");
    printf("%c%c\n", int_to_char_color[cube->stickers[20]], int_to_char_color[cube->stickers[21]]);
    printf("%c%c\n", int_to_char_color[cube->stickers[22]], int_to_char_color[cube->stickers[23]]);
}

/* --- BFS Solver --- */
static const char* MOVES[] = {"R", "R'", "R2", "U", "U'", "U2", "F", "F'", "F2"};
#define NUM_MOVES 9

typedef struct {
    BFSNode* queue;
    int head;
    int tail;
    int capacity;
} BFSQueue;

static BFSQueue* create_queue(int initial_capacity) {
    BFSQueue* q = malloc(sizeof(BFSQueue));
    q->queue = malloc(sizeof(BFSNode) * initial_capacity);
    q->head = 0;
    q->tail = 0;
    q->capacity = initial_capacity;
    return q;
}

static void enqueue(BFSQueue* q, const CubeState* state, int parent_idx, const char* move) {
    if (q->tail >= q->capacity) {
        /* Expand queue */
        q->capacity *= 2;
        q->queue = realloc(q->queue, sizeof(BFSNode) * q->capacity);
    }
    
    q->queue[q->tail].state = *state;
    q->queue[q->tail].parent_idx = parent_idx;
    q->queue[q->tail].move_from_parent = move;
    q->tail++;
}

static void solve_bfs(const CubeState* initial, int max_depth) {
    if (is_solved(initial)) {
        printf("Already Solved!\n");
        return;
    }
    
    /* Initialize visited table */
    memset(visited_table, 0, sizeof(visited_table));
    
    BFSQueue* q = create_queue(100000);
    
    /* Start with initial state */
    enqueue(q, initial, -1, NULL);
    mark_visited(initial);
    
    int depth = 0;
    int next_depth_node_idx = 1;
    int solution_idx = -1;
    
    while (q->head < q->tail && solution_idx == -1) {
        /* Check if we've processed all nodes at current depth */
        if (q->head >= next_depth_node_idx) {
            depth++;
            next_depth_node_idx = q->tail;
            
            fprintf(stderr, "Depth %d: explored %d nodes, queue size: %d\n", 
                    depth, q->head, q->tail);
            
            if (depth > max_depth) {
                fprintf(stderr, "Max depth reached without solution\n");
                break;
            }
        }
        
        BFSNode* current = &q->queue[q->head];
        q->head++;
        
        /* Try all moves */
        for (int i = 0; i < NUM_MOVES; i++) {
            CubeState next = apply_move(&current->state, MOVES[i]);
            
            if (mark_visited(&next)) {
                /* New state */
                if (is_solved(&next)) {
                    solution_idx = q->tail;
                    enqueue(q, &next, q->head - 1, MOVES[i]);
                    break;
                }
                
                enqueue(q, &next, q->head - 1, MOVES[i]);
            }
        }
    }
    
    if (solution_idx != -1) {
        /* Reconstruct solution */
        int* path_indices = malloc(sizeof(int) * (max_depth + 10));
        int path_len = 0;
        int idx = solution_idx;
        
        while (q->queue[idx].parent_idx != -1) {
            path_indices[path_len++] = idx;
            idx = q->queue[idx].parent_idx;
        }
        
        /* Print solution in reverse */
        printf("\nSolution (%d moves):\n", path_len);
        for (int i = path_len - 1; i >= 0; i--) {
            printf("%s ", q->queue[path_indices[i]].move_from_parent);
        }
        printf("\n");
        
        free(path_indices);
    } else {
        printf("No solution found.\n");
    }
    
    free(q->queue);
    free(q);
}

/* --- Main --- */
int main(int argc, char* argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <state_file>\n", argv[0]);
        return EXIT_FAILURE;
    }
    
    /* Initialize solved state */
    for (int i = 0; i < NUM_STICKERS; i++) {
        SOLVED_STATE.stickers[i] = char_to_int_color(SOLVED_STATE_STR[i]);
    }
    
    CubeState initial;
    parse_input_file(argv[1], &initial);
    
    printf("Initial state:\n");
    print_state(&initial);
    printf("\n");
    
    solve_bfs(&initial, 14);
    
    return EXIT_SUCCESS;
}
