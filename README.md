This is my documentation:

Note: in the project I maked the assumption that the roles where standardized. If they are not standardized i just tag them or gave them the level 0. if this is not the case i could have added a role mapping function with variations from the role name


First the Json is read.
The elements are read and classify if they are from 1 from the 2 types. (there could be more, in that case i just pass the "unknown structure" message)
Then those dicts are classified into type 1 or type 2. 
The "bezeichnung" or "qualifikation" is read and mapped with the dict of roles and levels.
Then the new list is created with dicts inside
The lists are saved and written in a new Json file

```mermaid
flowchart TD
    A[Start] --> B[main]
    B --> C[Read JSON file]
    C --> D[Process each nursing home]
    D --> E[process_nursing_home]
    E --> F{identify_json_type}
    F --> |Type 1| G[process_type1]
    F --> |Type 2| H[process_type2]
    G --> J[map_permission]
    H --> J
    J --> K[Create mapped data]
    K --> L[Return processed data]
    L --> M{All homes processed?}
    M --> |No| D
    M --> |Yes| N[Write results to JSON]
    N --> O[End]
    
    subgraph "map_permission function"
    J --> P{Check external role}
    P --> Q[Return permission level]
    end
```
