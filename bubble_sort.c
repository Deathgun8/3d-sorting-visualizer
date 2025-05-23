// bubble_sort.c
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define SIZE 50

void print_array(int arr[]) 
{
    for (int i = 0; i < SIZE; i++)
        printf("%d ", arr[i]);

    printf("\n");
}

int main() 
{
    int arr[SIZE];
    srand(time(NULL));

    for (int i = 0; i < SIZE; i++)
        arr[i] = rand() % 200 + 1;

    print_array(arr);

    for (int i = 0; i < SIZE - 1; i++) 
    {
        for (int j = 0; j < SIZE - i - 1; j++) 
        {
            if (arr[j] > arr[j + 1]) 
            {
                int tmp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = tmp;
                print_array(arr, SIZE);
            }
        }
    }
    return 0;
}