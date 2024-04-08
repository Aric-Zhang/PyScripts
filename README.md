# **Description of Python Assignment Portfolio**

During my university studies, the following single Python code files were developed to fulfill various Python homework assignments.

## **Assignment 1: Printing a Calendar in a Given Format**

This assignment involves two distinct implementations, stored in the files `Cal.py` and `Cal2.py`, respectively. Both programs are designed to output calendar information according to a specified format, potentially encompassing elements such as dates, weekdays, and markers for holidays, catering to diverse calendar presentation requirements.

## **Assignment 2: Simulating Bank Operations**

This task simulates the daily operations of a bank, incorporating three client types: corporate clients, private clients, and VIP clients. Each client type has distinct service time requirements. The bank operates multiple service windows, each initially designated to serve a particular client type. However, a window may switch to serving another client type once the demand for its initial type has been fully satisfied. Clients of different types queue in advance, and new clients continuously join the queues throughout the bank's operating hours.

Critical performance criteria include ensuring that the average waiting time for VIP clients does not exceed that of regular clients, and the average waiting time for corporate clients does not exceed that of private clients. The program should simulate and output the bank's customer service process over the course of a day, detailing events such as client arrivals, queuing, service initiation, and completion.

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
