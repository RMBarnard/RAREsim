cimport rsdec
from libc.stdint cimport uintptr_t
from libcpp cimport str

cdef class arrays:

    cdef rsdec.uint32_t_array *array32

    def array_destroy(self)-> void:
        uas = &(self.array32)
        rsdec.uint32_t_array_destroy(uas)

    def array_add(self, val)-> int:
        return rsdec.uint32_t_array_add( self.array32, val)

    def array_set(self, val,int index)-> int:
        return rsdec.uint32_t_array_set( self.array32,val, index)

    def array_get(self, int index)-> uintptr_t:
        return rsdec.uint32_t_array_get( self.array32, index)
    def array_write(self, filename)-> int:
        byte_file_name = filename.encode('UTF-8')
        cdef char* c_filename = byte_file_name
        return rsdec.uint32_t_array_write(self.array32, c_filename)

    def array_read(self, filename):
        byte_file_name = filename.encode('UTF-8')
        cdef char* c_filename = byte_file_name
        self.array32= rsdec.uint32_t_array_read(c_filename)

cdef class sparse:
    cdef rsdec.uint32_t_sparse_matrix *sparse32
    cdef char *path
    def __init__(self,path):
        p = to_bytes(path)
        self.path = p
        self.sparse32 = rsdec.read_matrix(to_bytes(p))

    def spars_matrix_add(self, row, val)-> int:
        return rsdec.uint32_t_sparse_matrix_add( self.sparse32, row, val)
    def spars_martix_get(self, row, col) -> uintptr_t:
        return rsdec.uint32_t_sparse_martix_get( self.sparse32, row, col)

    def spars_matrix_readbyline(self, byte_filename):
        cdef char* c_filename = byte_filename
        self.sparse32= rsdec.uint32_t_sparse_matrix_read( c_filename)

    def remove_row(self, row)->void:
        rsdec.uint32_t_sparse_martix_remove_row( self.sparse32,  row);
    def prune_row(self , row, num_prune) -> int:
        return rsdec.uint32_t_sparse_martix_prune_row( self.sparse32, row, num_prune)

    def read(self, byte_filename):
        cdef char* c_filename = byte_filename
        self.sparse32 =  rsdec.read_matrix( c_filename)

    def rcount(self)-> int:
        return rsdec.uint32_t_sparse_martix_num_rows(self.sparse32)
    def row_not_null(self, row)->int:
        return rsdec.uint32_t_sparse_martix_not_Null(self.sparse32, row)
    def write(self, outfile) -> void:
        byte_file_name = outfile.encode('UTF-8')
        cdef char* c_filename = byte_file_name
        rsdec.write_matrix( self.sparse32,c_filename)

cdef to_bytes(s, enc='UTF-8'):
    if not isinstance(s, bytes):
        return s.encode(enc)
    return s

cdef from_bytes(s):
    if isinstance(s, bytes):
      try:
          return s.decode('UTF-8')
      except UnicodeDecodeError:
          return s.decode('utf8', errors='replace')
    return s
