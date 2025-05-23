/* 
    Neste código o pivo é escolhido através da mediana de três
*/

#include <time.h>
#include <stdio.h>
#include <stdlib.h>

#define ARRAY_SIZE 50

void print_array(int arr[]);
void quick_sort(int arr[], int left, int right);
void swap(int arr[], int i, int j);
int partition(int arr[], int left, int right);
int pick_median_of_three_pivot(int arr[], int left, int right);

int main(void)
{
    int arr[ARRAY_SIZE];
    int i;

    srand(time(NULL));

    for(i = 0; i < ARRAY_SIZE; i++)
        arr[i] = rand() % 200 + 1;

    print_array(arr);

    quick_sort(arr, 0, ARRAY_SIZE - 1);
}

void print_array(int arr[])
{
    int i;

    for(i = 0; i < ARRAY_SIZE; i++)
        printf("%d ", arr[i]);

    printf("\n");
}

int pick_median_of_three_pivot(int arr[], int left, int right)
{
    int mid = left + (right - left) / 2;

    int a = arr[left];
    int b = arr[mid];
    int c = arr[right];

    // Encontra a mediana de a, b, c
    if ((a > b) != (a > c))
        return left;
    else 
        if ((b > a) != (b > c))
            return mid;
        else
            return right;
}

int partition(int arr[], int left, int right)
{
    int pivo_index = pick_median_of_three_pivot(arr, left, right);
    swap(arr, left, pivo_index);

    int pivo = arr[left];
    int i = left, j;

    for(j = left + 1; j <= right; j++)
    {
        if (arr[j] <= pivo)
        {
            i++;
            swap(arr, i, j);
        }
    }

    swap(arr, left, i);

    return i;
}

void quick_sort(int arr[], int left, int right)
{
    if (left < right)
    {
        int index_pivo = partition(arr, left, right);
        quick_sort(arr, left, index_pivo - 1);
        quick_sort(arr, index_pivo + 1, right);
        print_array(arr);
    }
}

void swap(int arr[], int i, int j)
{
    int temp = arr[i];
    arr[i] = arr[j];
    arr[j] = temp;
}