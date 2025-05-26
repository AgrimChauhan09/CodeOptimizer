#include <stdio.h>
#include <stdlib.h>

// string_processing implementation
int main() {
    // Implementation for string_processing
    int data[100];
    for (int i = 0; i < 100; i++) {
        data[i] = i * 2;
    }
    
    int result = 0;
    for (int i = 0; i < 100; i++) {
        result += data[i] * data[i];
    }
    
    printf("Result: %d\n", result);
    return 0;
}
