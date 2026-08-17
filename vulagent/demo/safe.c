#include <stdio.h>
#include <string.h>

void copy_input(char *input) {
    char buffer[64];
    if (strlen(input) < 64) {
        strcpy(buffer, input);
        printf("%s\n", buffer);
    }
}

int main(int argc, char **argv) {
    if (argc > 1) {
        copy_input(argv[1]);
    }
    return 0;
}
