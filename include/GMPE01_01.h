#define GW_STAT_LEN 52
#define GW_PLAYER_MAX 4

typedef struct GwPlayer_s {
/* 0x00 */ struct {
        u16 diff : 2;
        u16 com : 1;
        u16 character : 4;
        u16 auto_size : 2;
        u16 draw_ticket : 1;
        u16 ticket_player : 6;
    };
/* 0x02 */ struct {
        u8 team : 1;
        u8 spark : 1;
        u8 player_idx : 2;
    };
/* 0x03 */ s8 handicap;
/* 0x04 */ s8 port;
/* 0x05 */ s8 items[3];
/* 0x08 */ struct {
        u16 color : 2;
        u16 moving : 1;
        u16 jump : 1;
        u16 show_next : 1;
        u16 size : 2;
        u16 num_dice : 2;
        u16 rank : 2;
        u16 bowser_suit : 1;
        u16 team_backup : 1;
    };
/* 0x0A */ s8 roll;
/* 0x0C */ s16 space_curr;
/* 0x0E */ s16 space_prev;
/* 0x10 */ s16 space_next;
/* 0x12 */ s16 space_shock;
/* 0x14 */ s8 blue_count;
/* 0x15 */ s8 red_count;
/* 0x16 */ s8 question_count;
/* 0x17 */ s8 fortune_count;
/* 0x18 */ s8 bowser_count;
/* 0x19 */ s8 battle_count;
/* 0x1A */ s8 mushroom_count;
/* 0x1B */ s8 warp_count;
/* 0x1C */ s16 coins;
/* 0x1E */ s16 coins_mg;
/* 0x20 */ s16 coins_total;
/* 0x22 */ s16 coins_max;
/* 0x24 */ s16 coins_battle;
/* 0x26 */ s16 coin_collect;
/* 0x28 */ s16 coin_win;
/* 0x2A */ s16 stars;
/* 0x2C */ s16 stars_max;
/* 0x2E */ char unk_2E[2];
} GWPLAYER;

typedef struct GwSystem_s {
/* 0x00 */ struct {
        u8 party : 1;
        u8 team : 1;
    };
/* 0x01 */ u8 diff_story;
/* 0x02 */ struct {
        u16 bonus_star : 1;
        u16 explain_mg : 1;
        u16 show_com_mg : 1;
        u16 mg_list : 2;
        u16 mess_speed : 2;
        u16 save_mode : 2;
    };
/* 0x04 */ u8 turn;
/* 0x05 */ u8 max_turn;
/* 0x06 */ u8 star_flag;
/* 0x07 */ u8 star_total;
/* 0x08 */ struct {
    u8 star_pos : 3;
    u8 board : 5;
};
/* 0x09 */ s8 last5_effect;
/* 0x0A */ s8 player_curr;
/* 0x0B */ u8 storyCharBit;
/* 0x0C */ s8 storyChar;
/* 0x0E */ s16 block_pos;
/* 0x10 */ u8 board_data[32];
/* 0x30 */ u8 mess_delay;
/* 0x31 */ struct {
        u8 bowser_loss : 4;
        u8 bowser_event : 4;
    };
/* 0x32 */ s8 lucky_value;
/* 0x34 */ u16 mg_next;
/* 0x36 */ s16 mg_type;
/* 0x38 */ u16 unk_38;
/* 0x3A */ u8 flag[3][16];
/* 0x6A */ u8 unk_6A[0x72];
} GWSYSTEM; //8018fcf8, sizeof 0xDC

extern GWSYSTEM GWSystem;
extern GWPLAYER GWPlayer[GW_PLAYER_MAX];