# **Description of Python Assignment Portfolio**

During my university studies, the following single Python code files were developed to fulfill various Python homework assignments.

## **Assignment 1: Printing a Calendar in a Given Format**

This assignment involves two distinct implementations, stored in the files `Cal.py` and `Cal2.py`, respectively. Both programs are designed to output calendar information according to a specified format, potentially encompassing elements such as dates, weekdays, and markers for holidays, catering to diverse calendar presentation requirements.

## **Assignment 2: Simulating Bank Operations**

This is an exercise in numerical modeling involving Queueing Theory.

1. The bank possesses a total of 9 service windows.
2. Customers are categorized into three classes: corporate, VIP, and ordinary individuals. The average service speeds must adhere to the hierarchy corporate > VIP > ordinary individual.
3. At any point when there are customers of a given class waiting, at least one window must be dedicated to serving that class.
4. The bank operates for 8 hours, with approximately 30 people already waiting prior to opening, after which the expected number of waiting customers remains essentially constant.

Two versions of the implementation are provided, housed in the files `banktest.py` and `bank2.py`, respectively.

## **Assignment 3: Simulating the Working Principle of a FAT Hard Disk**

This assignment aims to emulate the file storage and retrieval mechanisms of a FAT (File Allocation Table) formatted hard disk. Key requirements include:

1. Creating a virtual FAT-formatted hard disk that mimics actual disk behavior through filesystem operations like writing and reading.
2. Properly managing disk space allocation during the simulation, adhering to the cluster allocation principles of the FAT table.
3. Providing a visual representation of the cluster occupancy on the simulated disk, offering a clear understanding of the storage status of a FAT hard disk.

Associated code files are as follows:

- `virtual_fat_disk.py`: Establishes a simulated FAT-format hard disk manifested as a file, supporting genuine file write and read operations.
- `disk_tester2.py`: Offers a graphical interface to dynamically depict cluster usage on the simulated hard disk, facilitating comprehension of FAT hard disk space allocation and utilization.
- `simu_fat.py`: Constitutes a simplified implementation focusing solely on simulating the principles of the FAT table, confined to printing cluster occupancy information. Lacking actual file access capabilities, this version serves to elucidate the FAT table logic unencumbered by complex filesystem interactions.
