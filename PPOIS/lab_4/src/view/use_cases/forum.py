from src.model.department import VirtualDepartment
from src.model.entities import ForumThread, Post, utc_now_iso
from src.model.exceptions import NotFoundError, ValidationError
from src.view.utils import new_id


def create_thread(dept: VirtualDepartment, title: str) -> ForumThread:
    title = title.strip()
    if not title:
        raise ValidationError("title is required")
    thread = ForumThread(thread_id=new_id("thr"), title=title)
    dept.threads[thread.thread_id] = thread
    return thread


def add_post(dept: VirtualDepartment, thread_id: str, author_id: str, content: str) -> Post:
    content = content.strip()
    if not content:
        raise ValidationError("content is required")
    thread = dept.threads.get(thread_id)
    if thread is None:
        raise NotFoundError(f"Thread '{thread_id}' not found")
    if author_id not in dept.students and author_id not in dept.teachers:
        raise NotFoundError(f"Author '{author_id}' not found")
    post = Post(author_id=author_id, content=content, created_at=utc_now_iso())
    thread.posts.append(post)
    return post


def list_threads(dept: VirtualDepartment) -> list[ForumThread]:
    return list(dept.threads.values())
