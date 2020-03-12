# Ansible role `cleanup_disconnect_active_sessions`

## Role tasks 

This role contains the following tasks:

<details>
<summary>cleanup_disconnect_active_sessions</summary>

### cleanup_disconnect_active_sessions

An Ansible role for disconnection all active session on a hosts list specified by `cleanup_disconnect_active_sessions_host_list` variable except system and Oracle users' sessions.

#### Role Variables

| Variable                                           | Required | Default                     | Description                                                       |
| :---                                               | :---     | :---                        | :---                                                              |
| `cleanup_disconnect_active_sessions_host_list`     | Yes      | -                           | A hosts list for active sessions to disconnect.                   |
| `cleanup_disconnect_active_sessions_file_dist_dir` | No       | `{{ infinys_dir }}/scripts` | A destination directory where disconnection SQL script is copied. |

</details>

<details>
<summary>cleanup_execute_sql_script</summary>

### cleanup_execute_sql_script

An Ansible role for resolving SQL script template specified by `cleanup_execute_sql_script_template_file` variable via SQL Plus utility on a hosts list specified by `cleanup_execute_sql_script_host_list` variable.

#### Role variables

| Variable                                   | Required | Default | Description                                         |
| :---                                       | :---     | :---    | :---                                                |
| `cleanup_execute_sql_script_template_file` | Yes      | -       | A path to SQL script template file.                 |
| `cleanup_execute_sql_script_dest_file`     | Yes      | -       | A path to result SQL script file.                   |
| `cleanup_execute_sql_script_host_list`     | Yes      | -       | A hosts list for the script file to be executed on. |

</details>

<details>
<summary>cleanup_rbm_database</summary>

### cleanup_rbm_database

An Ansible role for cleaning up a RBM database SQL on a hosts list specified by `cleanup_execute_sql_script_host_list` variable.

#### Role variables

| Variable                               | Required | Default                     | Description                                                     |
| :---                                   | :---     | :---                        | :---                                                            |
| `cleanup_execute_sql_script_host_list` | Yes      | -                           | A hosts list for a RBM database to be cleaned up.               |
| `cleanup_rbm_database_file_dest_dir`   | No       | `{{ infinys_dir }}/scripts` | A destination directory where cleaning up SQL script is copied. |

</details>

