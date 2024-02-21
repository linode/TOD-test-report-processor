def get_list_command(cluster):
    list_command = [
        "/usr/local/bin/linode-cli", "obj", "la",
        "--cluster", cluster,
    ]
    return list_command


def get_download_command(cluster, bucket, file_name, destination):
    download_command = [
        "/usr/local/bin/linode-cli", "obj", "get",
        "--cluster", cluster,
        bucket,
        file_name,
        destination,
    ]
    return download_command


def get_remove_command(cluster, bucket, file_name):
    remove_command = [
        "/usr/local/bin/linode-cli", "obj", "rm",
        "--cluster", cluster,
        bucket,
        file_name,
    ]
    return remove_command
