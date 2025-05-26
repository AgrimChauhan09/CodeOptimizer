#include <stdio.h>
#include <string.h>

int string_search(char* text, char* pattern) {
    int text_len = strlen(text);
    int pattern_len = strlen(pattern);
    
    for (int i = 0; i <= text_len - pattern_len; i++) {
        int j;
        for (j = 0; j < pattern_len; j++) {
            if (text[i + j] != pattern[j])
                break;
        }
        if (j == pattern_len)
            return i;
    }
    return -1;
}

int main() {
    char text[] = "ABABDABACDABABCABCABCABCABC";
    char pattern[] = "ABABCAB";
    
    int result = string_search(text, pattern);
    printf("Pattern found at index: %d\n", result);
    
    return 0;
}