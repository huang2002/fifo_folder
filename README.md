# fifo_folder

> A FIFO folder management library
> that manages files using queue-like principles.

## Install

```bash
pip install fifo_folder
```

## Example

Here's an example logger using `fifo_folder`
to limit the resources used by log files:

```python
import os

from fifo_folder import FIFOFolder

LOG_DIR_PATH = "/path/to/your/log/folder/"

log_manager = FIFOFolder(
    LOG_DIR_PATH,  # path to the folder to manage
    count_limit=100,  # keep at most 100 files
    total_size_limit=(1 << 30),  # keep sum of file sizes no greater than 1GB
)


def log(file_name: str, text: str) -> None:

    # create a new log file
    file_path = os.path.join(LOG_DIR_PATH, file_name)
    with open(file_path, "w") as file:
        file.write(text)

    log_manager.load_items()  # load current files
    removed_items = log_manager.manage()  # removed extra files
    if len(removed_items):  # display removed files
        print(
            "removed log files:",
            [os.path.basename(item.data.path) for item in removed_items]
        )
```

## Links

- [Documentation](https://github.com/huang2002/fifo_folder/wiki)
- [Changelog](https://github.com/huang2002/fifo_folder/blob/main/CHANGELOG.md)
- [License (ISC)](https://github.com/huang2002/fifo_folder/blob/main/LICENSE)
