from app.core.supabase_client import supabase, BUCKET_NAME


def upload_file(storage_path: str, file_bytes: bytes, content_type: str):
    """Upload file to Supabase Storage"""

    return supabase.storage.from_(BUCKET_NAME).upload(
        path=storage_path,
        file=file_bytes,
        file_options={
            "content-type": content_type
        }
    )


def download_file(storage_path: str):
    """Download file from Supabase Storage"""

    return supabase.storage.from_(BUCKET_NAME).download(storage_path)


def delete_file(storage_path: str):
    """Delete file from Supabase Storage"""

    return supabase.storage.from_(BUCKET_NAME).remove([storage_path])