import api  # must import to register package and execute its code.
import database


def main():
    api.app.start()


if __name__ == '__main__':
    main()

"""
Need to implement the following document objects:
    - OrderHistory ✓
    - Order ✓
        
    - Item ✓
    - Review ✓
    - StoreFormat ✓
    - ModificationButton ✓
    
    - Business ✓
    - Category ✓
    - Contact ✓
    
    - ImageGallery
        - Image
    
"""
