#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct { uint8_t s[24]; } CubeState;
const char* SOLVED_STATE_STR = "WWWWGGGGRRRRBBBBOOOOYYYY";
CubeState SOLVED;

static inline bool states_equal(const CubeState* a, const CubeState* b) {
    return memcmp(a->s, b->s, 24) == 0;
}

static uint32_t hash_state(const CubeState* a) {
    uint32_t h = 5381;
    for (int i = 0; i < 24; i++) h = ((h << 5) + h) + a->s[i];
    return h;
}

static void rotate_face(CubeState* state, int start) {
    uint8_t t = state->s[start];
    state->s[start] = state->s[start+2];
    state->s[start+2] = state->s[start+3];
    state->s[start+3] = state->s[start+1];
    state->s[start+1] = t;
}

static void apply_move(CubeState* s, char face) {
    CubeState old = *s;
    if (face == 'U') {
        rotate_face(s, 0);
        s->s[4] = old.s[8]; s->s[5] = old.s[9]; s->s[8] = old.s[12]; s->s[9] = old.s[13];
        s->s[12] = old.s[16]; s->s[13] = old.s[17]; s->s[16] = old.s[4]; s->s[17] = old.s[5];
    } else if (face == 'R') {
        rotate_face(s, 8);
        s->s[1] = old.s[15]; s->s[3] = old.s[13]; s->s[5] = old.s[1]; s->s[7] = old.s[3];
        s->s[21] = old.s[5]; s->s[23] = old.s[7]; s->s[15] = old.s[21]; s->s[13] = old.s[23];
    } else if (face == 'F') {
        rotate_face(s, 4);
        s->s[2] = old.s[17]; s->s[3] = old.s[19]; s->s[8] = old.s[2]; s->s[10] = old.s[3];
        s->s[20] = old.s[8]; s->s[21] = old.s[10]; s->s[17] = old.s[20]; s->s[19] = old.s[21];
    }
}

typedef struct { CubeState state; int parent; const char* move; char last; } Node;
#define TABLE_SIZE 10000003
typedef struct { CubeState state; int node_idx; bool occupied; } Entry;

static int visited(const CubeState* s, Entry* table) {
    uint32_t h = hash_state(s) % TABLE_SIZE;
    while (table[h].occupied) {
        if (states_equal(&table[h].state, s)) return table[h].node_idx;
        h = (h + 1) % TABLE_SIZE;
    }
    return -1;
}

static void add_visited(const CubeState* s, int node_idx, Entry* table) {
    uint32_t h = hash_state(s) % TABLE_SIZE;
    while (table[h].occupied) h = (h + 1) % TABLE_SIZE;
    table[h].state = *s; table[h].node_idx = node_idx; table[h].occupied = true;
}

const char* inv_move(const char* m) {
    if (strcmp(m, "U") == 0) return "U'"; if (strcmp(m, "U'") == 0) return "U";
    if (strcmp(m, "R") == 0) return "R'"; if (strcmp(m, "R'") == 0) return "R";
    if (strcmp(m, "F") == 0) return "F'"; if (strcmp(m, "F'") == 0) return "F";
    return m;
}

void solve_bidirectional(CubeState start) {
    if (states_equal(&start, &SOLVED)) { printf("\nSolution (0 moves):\n\n"); return; }
    
    Entry* table_fwd = calloc(TABLE_SIZE, sizeof(Entry));
    Entry* table_bwd = calloc(TABLE_SIZE, sizeof(Entry));
    int q_cap = 10000000;
    Node* q_fwd = malloc(sizeof(Node) * q_cap);
    Node* q_bwd = malloc(sizeof(Node) * q_cap);
    int h_fwd = 0, t_fwd = 0, h_bwd = 0, t_bwd = 0;
    
    q_fwd[t_fwd++] = (Node){start, -1, NULL, 0}; add_visited(&start, 0, table_fwd);
    q_bwd[t_bwd++] = (Node){SOLVED, -1, NULL, 0}; add_visited(&SOLVED, 0, table_bwd);
    
    const char* moves[] = {"U", "U'", "U2", "R", "R'", "R2", "F", "F'", "F2"};
    int sol_fwd = -1, sol_bwd = -1;
    
    for (int d = 0; d < 9; d++) {
        /* Forward step */
        int current_level_size = t_fwd - h_fwd;
        for (int i = 0; i < current_level_size; i++) {
            Node curr = q_fwd[h_fwd++];
            int curr_idx = h_fwd - 1;
            for (int m = 0; m < 9; m++) {
                if (moves[m][0] == curr.last) continue;
                CubeState next = curr.state;
                int count = (moves[m][1] == '\'') ? 3 : (moves[m][1] == '2' ? 2 : 1);
                for (int k = 0; k < count; k++) apply_move(&next, moves[m][0]);
                
                if (visited(&next, table_fwd) == -1) {
                    int bwd_idx = visited(&next, table_bwd);
                    if (bwd_idx != -1) { sol_fwd = t_fwd; sol_bwd = bwd_idx; 
                        q_fwd[t_fwd++] = (Node){next, curr_idx, moves[m], moves[m][0]}; goto found; }
                    if (t_fwd < q_cap) {
                        q_fwd[t_fwd++] = (Node){next, curr_idx, moves[m], moves[m][0]};
                        add_visited(&next, t_fwd - 1, table_fwd);
                    }
                }
            }
        }
        /* Backward step */
        current_level_size = t_bwd - h_bwd;
        for (int i = 0; i < current_level_size; i++) {
            Node curr = q_bwd[h_bwd++];
            int curr_idx = h_bwd - 1;
            for (int m = 0; m < 9; m++) {
                if (moves[m][0] == curr.last) continue;
                CubeState next = curr.state;
                int count = (moves[m][1] == '\'') ? 3 : (moves[m][1] == '2' ? 2 : 1);
                for (int k = 0; k < count; k++) apply_move(&next, moves[m][0]);
                
                if (visited(&next, table_bwd) == -1) {
                    int fwd_idx = visited(&next, table_fwd);
                    if (fwd_idx != -1) { sol_fwd = fwd_idx; sol_bwd = t_bwd;
                        q_bwd[t_bwd++] = (Node){next, curr_idx, moves[m], moves[m][0]}; goto found; }
                    if (t_bwd < q_cap) {
                        q_bwd[t_bwd++] = (Node){next, curr_idx, moves[m], moves[m][0]};
                        add_visited(&next, t_bwd - 1, table_bwd);
                    }
                }
            }
        }
    }
found:
    if (sol_fwd != -1) {
        int p1[64], l1 = 0, p2[64], l2 = 0;
        int i = sol_fwd; while (i != -1 && q_fwd[i].parent != -1) { p1[l1++] = i; i = q_fwd[i].parent; }
        if (i != -1 && q_fwd[i].move) p1[l1++] = i;
        i = sol_bwd; while (i != -1 && q_bwd[i].parent != -1) { p2[l2++] = i; i = q_bwd[i].parent; }
        if (i != -1 && q_bwd[i].move) p2[l2++] = i;

        printf("\nSolution (%d moves):\n", l1 + l2);
        for (int j = l1 - 1; j >= 0; j--) if(q_fwd[p1[j]].move) printf("%s ", q_fwd[p1[j]].move);
        for (int j = 0; j < l2; j++) if(q_bwd[p2[j]].move) printf("%s ", inv_move(q_bwd[p2[j]].move));
        printf("\n");
    } else printf("No solution found.\n");
    free(table_fwd); free(table_bwd); free(q_fwd); free(q_bwd);
}

int main(int argc, char** argv) {
    for (int i = 0; i < 24; i++) {
        char c = SOLVED_STATE_STR[i];
        SOLVED.s[i] = (c=='W'?0:c=='Y'?1:c=='R'?2:c=='O'?3:c=='B'?4:5);
    }
    if (argc != 2) return 1;
    FILE* f = fopen(argv[1], "r"); if (!f) return 1;
    CubeState start; char line[256];
    char* fl[6]; for (int i = 0; i < 6; i++) { fl[i] = malloc(256); fgets(fl[i], 256, f); }
    #define CC(c) (c=='W'?0:c=='Y'?1:c=='R'?2:c=='O'?3:c=='B'?4:5)
    start.s[0]=CC(fl[0][0]); start.s[1]=CC(fl[0][1]); start.s[2]=CC(fl[1][0]); start.s[3]=CC(fl[1][1]);
    start.s[16]=CC(fl[2][0]); start.s[17]=CC(fl[2][1]); start.s[4]=CC(fl[2][2]); start.s[5]=CC(fl[2][3]);
    start.s[8]=CC(fl[2][4]); start.s[9]=CC(fl[2][5]); start.s[12]=CC(fl[2][6]); start.s[13]=CC(fl[2][7]);
    start.s[18]=CC(fl[3][0]); start.s[19]=CC(fl[3][1]); start.s[6]=CC(fl[3][2]); start.s[7]=CC(fl[3][3]);
    start.s[10]=CC(fl[3][4]); start.s[11]=CC(fl[3][5]); start.s[14]=CC(fl[3][6]); start.s[15]=CC(fl[3][7]);
    start.s[20]=CC(fl[4][0]); start.s[21]=CC(fl[4][1]); start.s[22]=CC(fl[5][0]); start.s[23]=CC(fl[5][1]);
    for (int i = 0; i < 6; i++) free(fl[i]); fclose(f);
    solve_bidirectional(start); return 0;
}
