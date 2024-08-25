document.addEventListener('DOMContentLoaded', () => {
    document.body.addEventListener('click', (event) => {
        const button = event.target.closest('.comment-button');
        if (!button) return;

        const post = button.closest('.post');
        if (!post) return;

        const commentList = post.querySelector('.comment-list');
        const commentForm = post.querySelector('.comment-form');

        const commentListDisplay = getComputedStyle(commentList).display;
        const commentFormDisplay = getComputedStyle(commentForm).display;

        if (commentListDisplay === 'none' && commentFormDisplay === 'none') {
            commentList.style.display = 'inline-block';
            commentForm.style.display = 'flex';
            button.innerHTML = '<i class="fa-solid fa-comment"></i>';
        } else {
            commentList.style.display = 'none';
            commentForm.style.display = 'none';
            button.innerHTML = '<i class="fa-regular fa-comment"></i>';
        }
    });
});


document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.new-post');
    const textarea = document.querySelector('.new-post-ta');

    if (textarea) {
        textarea.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                form.submit();
            }
        });
    } else {
        console.info('The comment entry form was not found. The user may not be authorized.');
    }
});

