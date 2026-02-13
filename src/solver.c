#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

/* Compact state: 24 stickers, 3 bits each = 72 bits.
   BUT, we can fix one corner. Let's fix corner DFL (stickers 18, 6, 20).
   Actually, a simpler way to fix orientation is to only use U, R, F moves.
   If we only use U, R, F moves, the corner DLB (stickers 14, 19, 22 - wait, indexing?)
   Let's check indices from app.py:
   U: 0,1,2,3
   F: 4,5,6,7
   R: 8,9,10,11
   B: 12,13,14,15
   L: 16,17,18,19
   D: 20,21,22,23
   
   Corner DBL is (15, 19, 23).
   If we only use U, R, F moves, the DBL corner (15, 19, 23) never moves.
   So we have 7 corners left. Each corner has 3 stickers.
   7 corners * 3 stickers = 21 stickers.
   21 stickers * 3 bits = 63 bits. Fits in uint64_t!
   
   Stickers to exclude: 15 (B3), 19 (L3), 23 (D3).
*/

typedef uint64_t packed_state;

typedef struct { uint8_t s[24]; } CubeState;
const char* SOLVED_STATE_STR = "WWWWGGGGRRRRBBBBOOOOYYYY";
CubeState SOLVED;

static packed_state pack(const CubeState* cs) {
    packed_state res = 0;
    int bit = 0;
    for (int i = 0; i < 24; i++) {
        if (i == 15 || i == 19 || i == 23) continue;
        res |= ((packed_state)(cs->s[i] & 0x7)) << (bit * 3);
        bit++;
    }
    return res;
}

static inline bool states_equal(const CubeState* a, const CubeState* b) {
    return memcmp(a->s, b->s, 24) == 0;
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
        s->s[4] = old.s[8]; s->s[5] = old.s[9];
        s->s[8] = old.s[12]; s->s[9] = old.s[13];
        s->s[12] = old.s[16]; s->s[13] = old.s[17];
        s->s[16] = old.s[4]; s->s[17] = old.s[5];
    } else if (face == 'R') {
        rotate_face(s, 8);
        s->s[1] = old.s[15]; s->s[3] = old.s[13];
        s->s[5] = old.s[1]; s->s[7] = old.s[3];
        s->s[21] = old.s[5]; s->s[23] = old.s[7];
        s->s[15] = old.s[21]; s->s[13] = old.s[23];
    } else if (face == 'F') {
        rotate_face(s, 4);
        s->s[2] = old.s[17]; s->s[3] = old.s[19];
        s->s[8] = old.s[2]; s->s[10] = old.s[3];
        s->s[20] = old.s[8]; s->s[21] = old.s[10];
        s->s[17] = old.s[20]; s->s[19] = old.s[21];
    }
}

typedef struct { packed_state ps; int parent; const char* move; char last; } Node;
#define TABLE_SIZE 10000003
typedef struct { packed_state ps; int node_idx; bool occupied; } Entry;

static int visited(packed_state ps, Entry* table) {
    uint32_t h = (uint32_t)(ps ^ (ps >> 32)) % TABLE_SIZE;
    while (table[h].occupied) {
        if (table[h].ps == ps) return table[h].node_idx;
        h = (h + 1) % TABLE_SIZE;
    }
    return -1;
}

static void add_visited(packed_state ps, int node_idx, Entry* table) {
    uint32_t h = (uint32_t)(ps ^ (ps >> 32)) % TABLE_SIZE;
    while (table[h].occupied) h = (h + 1) % TABLE_SIZE;
    table[h].ps = ps; table[h].node_idx = node_idx; table[h].occupied = true;
}

const char* inv_move(const char* m) {
    if (m[1] == '2') return m;
    if (m[1] == '\'') { static char buf[2]; buf[0]=m[0]; buf[1]='\0'; return buf; }
    static char buf2[3]; buf2[0]=m[0]; buf2[1]='\''; buf2[2]='\0'; return buf2;
}

/* Hardcoded inverse moves because of static buffer issues */
const char* get_inv(const char* m) {
    if (strcmp(m, "U") == 0) return "U'"; if (strcmp(m, "U'") == 0) return "U";
    if (strcmp(m, "U2") == 0) return "U2";
    if (strcmp(m, "R") == 0) return "R'"; if (strcmp(m, "R'") == 0) return "R";
    if (strcmp(m, "R2") == 0) return "R2";
    if (strcmp(m, "F") == 0) return "F'"; if (strcmp(m, "F'") == 0) return "F";
    if (strcmp(m, "F2") == 0) return "F2";
    return m;
}

void solve_bidirectional(CubeState start) {
    packed_state start_ps = pack(&start);
    packed_state solved_ps = pack(&SOLVED);
    if (start_ps == solved_ps) { printf("\nSolution (0 moves):\n\n"); return; }
    
    Entry* table_fwd = calloc(TABLE_SIZE, sizeof(Entry));
    Entry* table_bwd = calloc(TABLE_SIZE, sizeof(Entry));
    int q_cap = 5000000;
    Node* q_fwd = malloc(sizeof(Node) * q_cap);
    Node* q_bwd = malloc(sizeof(Node) * q_cap);
    int h_fwd = 0, t_fwd = 0, h_bwd = 0, t_bwd = 0;
    
    q_fwd[t_fwd++] = (Node){start_ps, -1, NULL, 0}; add_visited(start_ps, 0, table_fwd);
    q_bwd[t_bwd++] = (Node){solved_ps, -1, NULL, 0}; add_visited(solved_ps, 0, table_bwd);
    
    const char* moves[] = {"U", "U'", "U2", "R", "R'", "R2", "F", "F'", "F2"};
    int sol_fwd = -1, sol_bwd = -1;
    
    for (int d = 0; d < 10; d++) {
        int lev_fwd = t_fwd - h_fwd;
        for (int i = 0; i < lev_fwd; i++) {
            int curr_idx = h_fwd++; Node curr = q_fwd[curr_idx];
            CubeState cs;
            /* Unpack briefly to apply move */
            int bit = 0;
            for (int j = 0; j < 24; j++) {
                if (j == 15 || j == 19 || j == 23) {
                    cs.s[j] = SOLVED.s[j]; // Fix corner
                } else {
                    cs.s[j] = (uint8_t)((curr.ps >> (bit * 3)) & 0x7);
                    bit++;
                }
            }
            for (int m = 0; m < 9; m++) {
                if (moves[m][0] == curr.last) continue;
                CubeState next_cs = cs;
                int count = (moves[m][1] == '\'') ? 3 : (moves[m][1] == '2' ? 2 : 1);
                for (int k = 0; k < count; k++) apply_move(&next_cs, moves[m][0]);
                packed_state nps = pack(&next_cs);
                if (visited(nps, table_fwd) == -1) {
                    int bidx = visited(nps, table_bwd);
                    if (bidx != -1) { sol_fwd = t_fwd; sol_bwd = bidx;
                        q_fwd[t_fwd++] = (Node){nps, curr_idx, moves[m], moves[m][0]}; goto found; }
                    if (t_fwd < q_cap) {
                        q_fwd[t_fwd++] = (Node){nps, curr_idx, moves[m], moves[m][0]};
                        add_visited(nps, t_fwd - 1, table_fwd);
                    }
                }
            }
        }
        int lev_bwd = t_bwd - h_bwd;
        for (int i = 0; i < lev_bwd; i++) {
            int curr_idx = h_bwd++; Node curr = q_bwd[curr_idx];
            CubeState cs;
            int bit = 0;
            for (int j = 0; j < 24; j++) {
                if (j == 15 || j == 19 || j == 23) cs.s[j] = SOLVED.s[j];
                else { cs.s[j] = (uint8_t)((curr.ps >> (bit * 3)) & 0x7); bit++; }
            }
            for (int m = 0; m < 9; m++) {
                if (moves[m][0] == curr.last) continue;
                CubeState next_cs = cs;
                int count = (moves[m][1] == '\'') ? 3 : (moves[m][1] == '2' ? 2 : 1);
                for (int k = 0; k < count; k++) apply_move(&next_cs, moves[m][0]);
                packed_state nps = pack(&next_cs);
                if (visited(nps, table_bwd) == -1) {
                    int fidx = visited(nps, table_fwd);
                    if (fidx != -1) { sol_fwd = fidx; sol_bwd = t_bwd;
                        q_bwd[t_bwd++] = (Node){nps, curr_idx, moves[m], moves[m][0]}; goto found; }
                    if (t_bwd < q_cap) {
                        q_bwd[t_bwd++] = (Node){nps, curr_idx, moves[m], moves[m][0]};
                        add_visited(nps, t_bwd - 1, table_bwd);
                    }
                }
            }
        }
    }
found:
    if (sol_fwd != -1) {
        int p1[64], l1 = 0, p2[64], l2 = 0;
        int idx = sol_fwd; while (idx != -1 && q_fwd[idx].parent != -1) { p1[l1++] = idx; idx = q_fwd[idx].parent; }
        if (idx != -1 && q_fwd[idx].move) p1[l1++] = idx;
        idx = sol_bwd; while (idx != -1 && q_bwd[idx].parent != -1) { p2[l2++] = idx; idx = q_bwd[idx].parent; }
        if (idx != -1 && q_bwd[idx].move) p2[l2++] = idx;
        printf("\nSolution (%d moves):\n", l1 + l2);
        for (int j = l1 - 1; j >= 0; j--) if(q_fwd[p1[j]].move) printf("%s ", q_fwd[p1[j]].move);
        for (int j = 0; j < l2; j++) if(q_bwd[p2[j]].move) printf("%s ", get_inv(q_bwd[p2[j]].move));
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
