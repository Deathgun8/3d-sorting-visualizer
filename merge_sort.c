#include <time.h>
#include <stdio.h>
#include <stdlib.h>

#define ARRAY_SIZE 50

void print_array(int arr[]);
void merge_sort(int arr[], int left, int right);
void merge(int arr[], int left, int middle, int right);

int main(void)
{
    int arr[ARRAY_SIZE];
    int i;

    //inicializa seed aleatoria
    srand(time(NULL));

    //Gera numeros aleatorios no array
    for (i = 0; i < ARRAY_SIZE; i++)
        arr[i] = rand() % 200 + 1;

    print_array(arr);

    merge_sort(arr, 0, ARRAY_SIZE - 1);
}

void print_array(int arr[])
{
    int i;

    for (i = 0; i < ARRAY_SIZE; i++)
        printf("%d ", arr[i]);

    printf("\n");
}

void merge_sort(int arr[], int left, int right)
{
    if(left < right)
    {
        int middle = left + (right - left) / 2;

        merge_sort(arr, left, middle);
        merge_sort(arr, middle + 1, right);

        merge(arr, left, middle, right);
        print_array(arr);
    }
}

void merge(int arr[], int left, int middle, int right)
{
    int i, j, k;
    int n1 = middle - left + 1;
    int n2 = right - middle;

    int L[n1], R[n2];

    for (i = 0; i < n1; i++)
        L[i] = arr[left + i];
    for (j = 0; j < n2; j++)
        R[j] = arr[middle + 1 + j];

    i = 0;
    j = 0;
    k = left;
    while (i < n1 && j < n2)
    {
        if (L[i] <= R[j])
        {
            arr[k] = L[i];
            i++;
        }
        else 
        {
            arr[k] = R[j];
            j++;
        }
        k++;
    }

    while (i < n1)
    {
        arr[k] = L[i];
        i++;
        k++;
    }

    while (j < n2)
    {
        arr[k] = R[j];
        j++;
        k++;
    }
}