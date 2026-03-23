"""Implementaciones manuales de varios algoritmos de ordenamiento.

Cada función recibe una lista (o arreglo) y devuelve una nueva lista ordenada.
Las implementaciones evitan el uso de funciones de ordenamiento de alto nivel
para cumplir con el enunciado del proyecto.

Nota: algunas implementaciones (por ejemplo TimSort simplificado o Bitonic)
están simplificadas pero funcionales para propósitos de benchmarking y enseñanza.
"""
from typing import List

# =========================================================
# 🔹 1. SELECTION SORT (Inicio)
# =========================================================
def selection_sort(arr: List[int]) -> List[int]:
    a = arr.copy()
    n = len(a)
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            if a[j] < a[min_idx]:
                min_idx = j
        a[i], a[min_idx] = a[min_idx], a[i]
    return a
# =========================================================
# 🔹 1. SELECTION SORT (Fin)
# =========================================================


# =========================================================
# 🔹 2. BINARY INSERTION SORT (Inicio)
# =========================================================
def binary_insertion_sort(arr: List[int]) -> List[int]:
    a = []
    for x in arr:
        lo, hi = 0, len(a)
        while lo < hi:
            mid = (lo + hi) // 2
            if a[mid] < x:
                lo = mid + 1
            else:
                hi = mid
        a.insert(lo, x)
    return a
# =========================================================
# 🔹 2. BINARY INSERTION SORT (Fin)
# =========================================================


# =========================================================
# 🔹 3. GNOME SORT (Inicio)
# =========================================================
def gnome_sort(arr: List[int]) -> List[int]:
    a = arr.copy()
    i = 1
    while i < len(a):
        if a[i] >= a[i-1]:
            i += 1
        else:
            a[i], a[i-1] = a[i-1], a[i]
            if i > 1:
                i -= 1
    return a
# =========================================================
# 🔹 3. GNOME SORT (Fin)
# =========================================================


# =========================================================
# 🔹 4. COMB SORT (Inicio)
# =========================================================
def comb_sort(arr: List[int]) -> List[int]:
    a = arr.copy()
    n = len(a)
    gap = n
    shrink = 1.3
    sorted_flag = False
    while not sorted_flag:
        gap = int(gap / shrink)
        if gap <= 1:
            gap = 1
            sorted_flag = True
        i = 0
        while i + gap < n:
            if a[i] > a[i+gap]:
                a[i], a[i+gap] = a[i+gap], a[i]
                sorted_flag = False
            i += 1
    return a
# =========================================================
# 🔹 4. COMB SORT (Fin)
# =========================================================


# =========================================================
# 🔹 5. QUICK SORT (Inicio)
# =========================================================
def quick_sort(arr: List[int]) -> List[int]:
    if len(arr) <= 1:
        return arr.copy()
    pivot = arr[len(arr)//2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
# =========================================================
# 🔹 5. QUICK SORT (Fin)
# =========================================================


# =========================================================
# 🔹 6. HEAP SORT (Inicio)
# =========================================================
def heap_sort(arr: List[int]) -> List[int]:
    a = arr.copy()
    n = len(a)

    # Construir el heap (max-heap)
    for i in range(n // 2 - 1, -1, -1):
        heapify(a, n, i)

    # Extraer elementos uno por uno
    for i in range(n - 1, 0, -1):
        # Mover la raíz (máximo) al final
        a[i], a[0] = a[0], a[i]

        # Volver a ajustar el heap
        heapify(a, i, 0)

    return a


def heapify(a: List[int], n: int, i: int):
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2

    # Si el hijo izquierdo es mayor
    if left < n and a[left] > a[largest]:
        largest = left

    # Si el hijo derecho es mayor
    if right < n and a[right] > a[largest]:
        largest = right

    # Si el mayor no es la raíz
    if largest != i:
        a[i], a[largest] = a[largest], a[i]
        heapify(a, n, largest)
# =========================================================
# 🔹 6. HEAP SORT (Fin)
# =========================================================


# =========================================================
# 🔹 7. TREE SORT (Inicio)
# =========================================================
class _BSTNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

def _bst_insert(root, val):
    if root is None:
        return _BSTNode(val)
    if val < root.val:
        root.left = _bst_insert(root.left, val)
    else:
        root.right = _bst_insert(root.right, val)
    return root

def _bst_inorder(root, out):
    if root is None:
        return
    _bst_inorder(root.left, out)
    out.append(root.val)
    _bst_inorder(root.right, out)

def tree_sort(arr: List[int]) -> List[int]:
    root = None
    for x in arr:
        root = _bst_insert(root, x)
    out = []
    _bst_inorder(root, out)
    return out
# =========================================================
# 🔹 7. TREE SORT (Fin)
# =========================================================


# =========================================================
# 🔹 8. PIGEONHOLE SORT (Inicio)
# =========================================================
def pigeonhole_sort(arr: List[int]) -> List[int]:
    if not arr:
        return []
    min_val = min(arr)
    max_val = max(arr)
    size = max_val - min_val + 1
    holes = [0] * size
    for x in arr:
        holes[x - min_val] += 1
    out = []
    for i in range(size):
        out.extend([i + min_val] * holes[i])
    return out
# =========================================================
# 🔹 8. PIGEONHOLE SORT (Fin)
# =========================================================


# =========================================================
# 🔹 9. BUCKET SORT (Inicio)
# =========================================================
def insertion_sort(arr: List[int]) -> List[int]:
    a = []
    for x in arr:
        a.append(x)

    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key

    return a


def bucket_sort(arr: List[int], bucket_size: int = 1000) -> List[int]:
    if len(arr) == 0:
        return []

    # Copia manual
    a = []
    for x in arr:
        a.append(x)

    # Min y max manual
    min_val = a[0]
    max_val = a[0]
    for x in a:
        if x < min_val:
            min_val = x
        if x > max_val:
            max_val = x

    # Crear buckets manualmente
    bucket_count = (max_val - min_val) // bucket_size + 1
    buckets = []
    for _ in range(bucket_count):
        buckets.append([])

    # Distribución
    for x in a:
        idx = (x - min_val) // bucket_size
        buckets[idx].append(x)

    # Ordenar y unir manualmente
    out = []
    for b in buckets:
        if len(b) > 0:
            sorted_bucket = insertion_sort(b)
            for val in sorted_bucket:
                out.append(val)

    return out
# =========================================================
# 🔹 9. BUCKET SORT (Fin)
# =========================================================


# =========================================================
# 🔹 10. RADIX SORT (Inicio)
# =========================================================
def radix_sort(arr: List[int]) -> List[int]:
    if not arr:
        return []
    if any(x < 0 for x in arr):
        offset = -min(arr)
        arr = [x + offset for x in arr]
    else:
        offset = 0

    max_val = max(arr)
    exp = 1
    a = arr.copy()
    while max_val // exp > 0:
        buckets = [[] for _ in range(10)]
        for x in a:
            buckets[(x // exp) % 10].append(x)
        a = []
        for b in buckets:
            a.extend(b)
        exp *= 10

    if offset:
        a = [x - offset for x in a]
    return a
# =========================================================
# 🔹 10. RADIX SORT (Fin)
# =========================================================


# =========================================================
# 🔹 11. BITONIC SORT (Inicio)
# =========================================================
def _bitonic_merge(a, low, cnt, direction):
    if cnt > 1:
        k = cnt // 2
        for i in range(low, low + k):
            if (direction == 1 and a[i] > a[i + k]) or (direction == 0 and a[i] < a[i + k]):
                a[i], a[i + k] = a[i + k], a[i]
        _bitonic_merge(a, low, k, direction)
        _bitonic_merge(a, low + k, k, direction)

def _bitonic_sort(a, low, cnt, direction):
    if cnt > 1:
        k = cnt // 2
        _bitonic_sort(a, low, k, 1)
        _bitonic_sort(a, low + k, k, 0)
        _bitonic_merge(a, low, cnt, direction)

def bitonic_sort(arr: List[int]) -> List[int]:
    a = arr.copy()
    n = len(a)
    if n == 0:
        return []
    pow2 = 1
    while pow2 < n:
        pow2 <<= 1
    pad_value = max(a) + 1
    a.extend([pad_value] * (pow2 - n))
    _bitonic_sort(a, 0, pow2, 1)
    return [x for x in a if x != pad_value][:n]
# =========================================================
# 🔹 11. BITONIC SORT (Fin)
# =========================================================


# =========================================================
# 🔹 12. TIM SORT (Inicio)
# =========================================================
def tim_sort(arr: List[int]) -> List[int]:
    MIN_RUN = 32

    def insertion_sort(sub):
        for i in range(1, len(sub)):
            key = sub[i]
            j = i - 1
            while j >= 0 and sub[j] > key:
                sub[j+1] = sub[j]
                j -= 1
            sub[j+1] = key
        return sub

    def merge(left, right):
        i = j = 0
        out = []
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                out.append(left[i]); i += 1
            else:
                out.append(right[j]); j += 1
        out.extend(left[i:]); out.extend(right[j:])
        return out

    n = len(arr)
    if n <= MIN_RUN:
        return insertion_sort(arr.copy())

    runs = []
    i = 0
    while i < n:
        j = min(i + MIN_RUN, n)
        run = insertion_sort(arr[i:j].copy())
        runs.append(run)
        i = j

    while len(runs) > 1:
        new_runs = []
        for k in range(0, len(runs), 2):
            if k+1 < len(runs):
                new_runs.append(merge(runs[k], runs[k+1]))
            else:
                new_runs.append(runs[k])
        runs = new_runs

    return runs[0] if runs else []
# =========================================================
# 🔹 12. TIM SORT (Fin)
# =========================================================


# Registry of algorithms for easy access
ALGORITHMS = {
    'SelectionSort': selection_sort,
    'BinaryInsertionSort': binary_insertion_sort,
    'GnomeSort': gnome_sort,
    'CombSort': comb_sort,
    'QuickSort': quick_sort,
    'HeapSort': heap_sort,
    'TreeSort': tree_sort,
    'PigeonholeSort': pigeonhole_sort,
    'BucketSort': bucket_sort,
    'RadixSort': radix_sort,
    'BitonicSort': bitonic_sort,
    'TimSort': tim_sort,
}
