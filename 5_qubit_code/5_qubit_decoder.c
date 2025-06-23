#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

bool flag;
struct dictionary
{
    int syndrome[4];
    char *correction;
};

char *syndrome1(bool flag);
char *syndrome2(bool flag);
char *syndrome3(bool flag);
char *syndrome4(bool flag);

int main()
{
    int n;
    scanf("%d", &n);
    if (n == 1)
        flag = false;
    else if (n == -1)
        flag = true;
    else
    {
        printf("Incorrect Flag Measurement.\n");
        exit(1);
    }

    char *correction1, *correction2, *correction3, *correction4; 
    if ((correction1 = malloc(sizeof(char) * 6)) == NULL)
    {
        printf("Correction 1 Allocation Failed.\n");
        exit(1);
    }
    if ((correction2 = malloc(sizeof(char) * 6)) == NULL)
    {
        printf("Correction 2 Allocation Failed.\n");
        exit(1);
    }
    if ((correction3 = malloc(sizeof(char) * 6)) == NULL)
    {
        printf("Correction 3 Allocation Failed.\n");
        exit(1);
    }
    if ((correction4 = malloc(sizeof(char) * 6)) == NULL)
    {
        printf("Correction 4 Allocation Failed.\n");
        exit(1);
    }

    if ((correction1 = syndrome1(flag)) == NULL)
    {
        printf("No valid correction for syndrome measurement 1.\n");
        exit(1);
    }
    if ((correction2 = syndrome2(flag)) == NULL)
    {
        printf("No valid correction for syndrome measurement 2.\n");
        exit(1);
    }
    if ((correction3 = syndrome3(flag)) == NULL)
    {
        printf("No valid correction for syndrome measurement 3.\n");
        exit(1);
    }
    if ((correction4 = syndrome4(flag)) == NULL)
    {
        printf("No valid correction for syndrome measurement 4.\n");
        exit(1);
    }

    free(correction1);
    free(correction2);
    free(correction3);
    free(correction4);
    return 0;
}

char *syndrome1(bool flag)
{
    // Measuring XZZXI
    int syndrome[4];
    int *p = syndrome;
    for (; p < syndrome + 4; p++)
    {
        scanf(" %d", p++);
        if (abs(*p) != 1)
        {
            printf("Incorrect Stabilizer Measurement Outcome.\n");
            exit(1);
        }
    }

    if (flag)
    {
        struct dictionary dict[] = {[0] = { .syndrome = {1, 1, 1, 1}, .correction = "IIIII"},
                                    [1] = { .syndrome = {-1, -1, 1, 1}, .correction = "IXZXI"},
                                    [2] = { .syndrome = {-1, 1, 1, -1}, .correction = "IYZXI"},
                                    [3] = { .syndrome = {1, 1, 1, -1}, .correction = "IZZXI"},
                                    [4] = { .syndrome = {1, -1, -1, 1}, .correction = "IIIXI"},
                                    [5] = { .syndrome = {-1, 1, -1, 1}, .correction = "IIXXI"},
                                    [6] = { .syndrome = {-1, 1, 1, 1}, .correction = "IIYXI"},
                                    [7] = { .syndrome = {1, -1, 1, 1}, .correction = "IIZXI"}};

        int i, j;
        for (i = 0; i < 8; i++)
        {
            for (j = 0; j < 4; j++)
            {
                if (dict[i].syndrome[j] != syndrome[j])
                    break;
            }
            if (j == 4)
                return dict[i].correction;
        }
        return NULL;
    }
    else
    {
        struct dictionary dict[] = {[0] = { .syndrome = {1, 1, 1, 1}, .correction = "IIIII"},
                                    [1] = { .syndrome = {1, 1, 1, -1}, .correction = "XIIII"},
                                    [2] = { .syndrome = {-1, 1, -1, -1}, .correction = "YIIII"},
                                    [3] = { .syndrome = {-1, 1, -1 ,1}, .correction = "ZIIII"},
                                    [4] = { .syndrome = {-1, 1, 1, 1}, .correction = "IXIII"},
                                    [5] = { .syndrome = {-1, -1, 1, -1}, .correction = "IYIII"},
                                    [6] = { .syndrome = {1, -1, 1, -1}, .correction = "IZIII"},
                                    [7] = { .syndrome = {-1, -1, 1, 1}, .correction = "IIXII"},
                                    [8] = { .syndrome = {-1, -1, -1, 1}, .correction = "IIYII"},
                                    [9] = { .syndrome = {1, 1, -1, 1}, .correction = "IIZII"},
                                    [10] = { .syndrome = {1, -1, -1 ,1}, .correction = "IIIXI"},
                                    [11] = { .syndrome = {-1, -1, -1, -1}, .correction = "IIIYI"},
                                    [12] = { .syndrome = {-1, 1, 1, -1}, .correction = "IIIZI"}};

        int i, j;
        for (i = 0; i < 13; i++)
        {
            for (j = 0; j < 4; j++)
            {
                if (dict[i].syndrome[j] != syndrome[j])
                    break;
            }
            if (j == 4)
                return dict[i].correction;
        }
        return NULL;
    }
}


char *syndrome2(bool flag)
{
    // Measuring IXZZX
    int syndrome[4];
    int *p = syndrome;
    for (; p < syndrome + 4; p++)
    {
        scanf(" %d", p++);
        if (abs(*p) != 1)
        {
            printf("Incorrect Stabilizer Measurement Outcome.\n");
            exit(1);
        }
    }

    if (flag)
    {
        struct dictionary dict[] = {[0] = { .syndrome = {1, 1, 1, 1}, .correction = "IIIII"},
                                    [1] = { .syndrome = {-1, 1, -1, 1}, .correction = "IIIZX"},
                                    [2] = { .syndrome = {1, -1, -1, 1}, .correction = "IIXZX"},
                                    [3] = { .syndrome = {1, -1, 1, 1}, .correction = "IIYZX"},
                                    [4] = { .syndrome = {-1, 1, 1, 1}, .correction = "IIZZX"},
                                    [5] = { .syndrome = {1, 1, -1, -1}, .correction = "IIIIX"},
                                    [6] = { .syndrome = {1, -1, 1, -1}, .correction = "IIIXX"},
                                    [7] = { .syndrome = {-1, -1, 1, 1}, .correction = "IIIYX"}};

        int i, j;
        for (i = 0; i < 8; i++)
        {
            for (j = 0; j < 4; j++)
            {
                if (dict[i].syndrome[j] != syndrome[j])
                    break;
            }
            if (j == 4)
                return dict[i].correction;
        }
        return NULL;
    }
    else
    {
        struct dictionary dict[] = {[0] = { .syndrome = {1, 1, 1, 1}, .correction = "IIIII"},
                                    [1] = { .syndrome = {-1, 1, 1, 1}, .correction = "IXIII"},
                                    [2] = { .syndrome = {-1, -1, 1, -1}, .correction = "IYIII"},
                                    [3] = { .syndrome = {1, -1, 1, -1}, .correction = "IZIII"},
                                    [4] = { .syndrome = {-1, -1, 1, 1}, .correction = "IIXII"},
                                    [5] = { .syndrome = {-1, -1, -1, 1}, .correction = "IIYII"},
                                    [6] = { .syndrome = {1, 1, -1, 1}, .correction = "IIZII"},
                                    [7] = { .syndrome = {1, -1, -1, 1}, .correction = "IIIXI"},
                                    [8] = { .syndrome = {-1, -1, -1, -1}, .correction = "IIIYI"},
                                    [9] = { .syndrome = {-1, 1, 1, -1}, .correction = "IIIZI"},
                                    [10] = { .syndrome = {1, 1, -1, -1}, .correction = "IIIIX"},
                                    [11] = { .syndrome = {1, -1, -1, -1}, .correction = "IIIIY"},
                                    [12] = { .syndrome = {1, -1, 1, 1}, .correction = "IIIIZ"}};

        int i, j;
        for (i = 0; i < 13; i++)
        {
            for (j = 0; j < 4; j++)
            {
                if (dict[i].syndrome[j] != syndrome[j])
                    break;
            }
            if (j == 4)
                return dict[i].correction;
        }
        return NULL;
    }
}


char *syndrome3(bool flag)
{
    // Measuring XIXZZ
    int syndrome[4];
    int *p = syndrome;
    for (; p < syndrome + 4; p++)
    {
        scanf(" %d", p++);
        if (abs(*p) != 1)
        {
            printf("Incorrect Stabilizer Measurement Outcome.\n");
            exit(1);
        }
    }

    if (flag)
    {
        struct dictionary dict[] = {[0] = { .syndrome = {1, 1, 1, 1}, .correction = "IIIII"},
                                    [1] = { .syndrome = {-1, -1, 1, -1}, .correction = "IIIZZ"},
                                    [2] = { .syndrome = {1, 1, 1, -1}, .correction = "IIXZZ"},
                                    [3] = { .syndrome = {1, 1, -1, -1}, .correction = "IIYZZ"},
                                    [4] = { .syndrome = {-1, -1, -1, -1}, .correction = "IIZZZ"},
                                    [5] = { .syndrome = {1, -1, 1, 1}, .correction = "IIIIZ"},
                                    [6] = { .syndrome = {1, 1, -1, 1}, .correction = "IIIXZ"},
                                    [7] = { .syndrome = {-1, 1, -1, -1}, .correction = "IIIYZ"}};

        int i, j;
        for (i = 0; i < 8; i++)
        {
            for (j = 0; j < 4; j++)
            {
                if (dict[i].syndrome[j] != syndrome[j])
                    break;
            }
            if (j == 4)
                return dict[i].correction;
        }
        return NULL;
    }
    else
    {
        struct dictionary dict[] = {[0] = { .syndrome = {1, 1, 1, 1}, .correction = "IIIII"},
                                    [1] = { .syndrome = {1, 1, 1, -1}, .correction = "XIIII"},
                                    [2] = { .syndrome = {-1, 1, -1, -1}, .correction = "YIIII"},
                                    [3] = { .syndrome = {-1, 1, -1 ,1}, .correction = "ZIIII"},
                                    [4] = { .syndrome = {-1, -1, 1, 1}, .correction = "IIXII"},
                                    [5] = { .syndrome = {-1, -1, -1, 1}, .correction = "IIYII"},
                                    [6] = { .syndrome = {1, 1, -1, 1}, .correction = "IIZII"},
                                    [7] = { .syndrome = {1, -1, -1, 1}, .correction = "IIIXI"},
                                    [8] = { .syndrome = {-1, -1, -1, -1}, .correction = "IIIYI"},
                                    [9] = { .syndrome = {-1, 1, 1, -1}, .correction = "IIIZI"},
                                    [10] = { .syndrome = {1, 1, -1, -1}, .correction = "IIIIX"},
                                    [11] = { .syndrome = {1, -1, -1, -1}, .correction = "IIIIY"},
                                    [12] = { .syndrome = {1, -1, 1, 1}, .correction = "IIIIZ"}};

        int i, j;
        for (i = 0; i < 13; i++)
        {
            for (j = 0; j < 4; j++)
            {
                if (dict[i].syndrome[j] != syndrome[j])
                    break;
            }
            if (j == 4)
                return dict[i].correction;
        }
        return NULL;
    }
}


char *syndrome4(bool flag)
{
    // Measuring ZXIXZ
    int syndrome[4];
    int *p = syndrome;
    for (; p < syndrome + 4; p++)
    {
        scanf(" %d", p++);
        if (abs(*p) != 1)
        {
            printf("Incorrect Stabilizer Measurement Outcome.\n");
            exit(1);
        }
    }

    if (flag)
    {
        struct dictionary dict[] = {[0] = { .syndrome = {1, 1, 1, 1}, .correction = "IIIII"},
                                    [1] = { .syndrome = {1, 1, -1, 1}, .correction = "IIIXZ"},
                                    [2] = { .syndrome = {-1, 1, -1, 1}, .correction = "IXIXZ"},
                                    [3] = { .syndrome = {-1, -1, -1, -1}, .correction = "IYIXZ"},
                                    [4] = { .syndrome = {1, -1, -1, -1}, .correction = "IZIXZ"},
                                    [5] = { .syndrome = {1, -1, 1, 1}, .correction = "IIIIZ"},
                                    [6] = { .syndrome = {-1, 1, -1, -1}, .correction = "IIIYZ"},
                                    [7] = { .syndrome = {-1, -1, 1, -1}, .correction = "IIIZZ"}};

        int i, j;
        for (i = 0; i < 8; i++)
        {
            for (j = 0; j < 4; j++)
            {
                if (dict[i].syndrome[j] != syndrome[j])
                    break;
            }
            if (j == 4)
                return dict[i].correction;
        }
        return NULL;
    }
    else
    {
        struct dictionary dict[] = {[0] = { .syndrome = {1, 1, 1, 1}, .correction = "IIIII"},
                                    [1] = { .syndrome = {1, 1, 1, -1}, .correction = "XIIII"},
                                    [2] = { .syndrome = {-1, 1, -1, -1}, .correction = "YIIII"},
                                    [3] = { .syndrome = {-1, 1, -1, 1}, .correction = "ZIIII"},
                                    [4] = { .syndrome = {-1, 1, 1, 1}, .correction = "IXIII"},
                                    [5] = { .syndrome = {-1, -1, 1, -1}, .correction = "IYIII"},
                                    [6] = { .syndrome = {1, -1, 1, -1}, .correction = "IZIII"},
                                    [7] = { .syndrome = {1, -1, -1, 1}, .correction = "IIIXI"},
                                    [8] = { .syndrome = {-1, -1, -1, -1}, .correction = "IIIYI"},
                                    [9] = { .syndrome = {-1, 1, 1, -1}, .correction = "IIIZI"},
                                    [10] = { .syndrome = {1, 1, -1, -1}, .correction = "IIIIX"},
                                    [11] = { .syndrome = {1, -1, -1, -1}, .correction = "IIIIY"},
                                    [12] = { .syndrome = {1, -1, 1, 1}, .correction = "IIIIZ"}};

        int i, j;
        for (i = 0; i < 13; i++)
        {
            for (j = 0; j < 4; j++)
            {
                if (dict[i].syndrome[j] != syndrome[j])
                    break;
            }
            if (j == 4)
                return dict[i].correction;
        }
        return NULL;
    }
}