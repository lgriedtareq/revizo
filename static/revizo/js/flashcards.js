document.addEventListener('DOMContentLoaded', function() {
    const config = {
        urls: window.REVIZO_URLS || {}        
    };

    console.log('Configuration loaded:', config);

    // Ensure we have the required URLs
    if (!config.urls.getTopics) {
        console.error('Missing getTopics URL configuration');
        return;
    }

    initSubjectFilters();
    initTopicFilters();
    initCardActions();
    initModal();
    initModalSubjectFilter();

    function initSubjectFilters() {
        document.getElementById('subject').addEventListener('change', function() {
            const subjectId = this.value;
            const topicSelect = document.getElementById('topic');
            topicSelect.innerHTML = '<option value="">-- Select --</option>';
            
            if (subjectId) {
                console.log('Fetching topics for subject:', subjectId);
                fetchTopics(subjectId, topicSelect);
            }
        });

        const initialSubject = document.getElementById('subject').value;
        if (initialSubject) {
            fetchTopics(initialSubject, document.getElementById('topic'));
        }
    }

    function initTopicFilters() {
        const topicSelect = document.getElementById('topic');
        
        topicSelect.addEventListener('change', function() {
            const topicId = this.value;
            if (topicId) {
                fetch(`${config.urls.filterCards}?topic_id=${topicId}`, {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCSRFToken()
                    },
                    credentials: 'same-origin'
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => updateCardTable(data.flashcards))
                .catch(error => {
                    console.error('Error:', error);
                    showToast('Error loading cards: ' + error.message, 'error');
                });
            }
        });
    }

    function initModalSubjectFilter() {
        document.getElementById('modal-subject').addEventListener('change', function() {
            const subjectId = this.value;
            const modalTopicSelect = document.getElementById('modal-topic');
            modalTopicSelect.innerHTML = '<option value="">-- Select --</option>';
            
            if (subjectId) {
                fetchTopics(subjectId, modalTopicSelect);
            }
        });
    }

    function initModal() {
        const modal = document.getElementById('addCardModal');
        const closeModal = () => modal.classList.remove('show');

        document.querySelector('[data-target="#addCardModal"]').addEventListener('click', () => {
            modal.classList.add('show');
        });

        modal.querySelectorAll('[data-dismiss="modal"]').forEach(btn => {
            btn.addEventListener('click', closeModal);
        });

        document.getElementById('addCardForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            
            fetch(config.urls.addCard, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                },
                body: formData
            })
            .then(handleResponse)
            .then(() => {
                closeModal();
                this.reset();
                document.getElementById('topic').dispatchEvent(new Event('change'));
                showToast('Card added successfully');
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Failed to add card', 'error');
            });
        });
    }

    function fetchTopics(subjectId, targetElement) {
        if (!subjectId) {
            console.error('No subject ID provided');
            return;
        }

        let url = config.urls.getTopics;
        
        url = `${url}?subject_id=${subjectId}`;
        console.log('Fetching topics from URL:', url);
        
        fetch(url, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        })
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Received topics data:', data);
            targetElement.innerHTML = '<option value="">-- Select Topic --</option>';
            
            if (Array.isArray(data)) {
                data.forEach(topic => {
                    const option = document.createElement('option');
                    option.value = topic.id;
                    option.textContent = topic.topic_name;
                    targetElement.appendChild(option);
                });
            } else {
                console.error('Expected array of topics but got:', typeof data, data);
                throw new Error('Invalid data format received from server');
            }
        })
        .catch(error => {
            console.error('Error fetching topics:', error);
            targetElement.innerHTML = '<option value="">Error loading topics</option>';
            showToast('Error loading topics: ' + error.message, 'error');
        });
    }

    function updateCardTable(cards) {
        const tbody = document.querySelector('table tbody');
        tbody.innerHTML = cards.length > 0 ? 
            cards.map(card => `
                <tr id="card-${card.id}">
                    <td>${card.subject_name || ''}</td>
                    <td>${card.topic_name || ''}</td>
                    <td contenteditable="true" class="editable" data-field="card_front">${card.card_front}</td>
                    <td contenteditable="true" class="editable" data-field="card_back">${card.card_back}</td>
                    <td>
                        <button class="btn btn-primary btn-sm save-card">💾 Save</button>
                        <button class="btn btn-danger btn-sm delete-card">❌ Delete</button>
                    </td>
                </tr>
            `).join('') :
            '<tr><td colspan="5" class="text-center">No flashcards found</td></tr>';
    }

    function initCardActions() {
        document.querySelector('table').addEventListener('click', function(e) {
            const row = e.target.closest('tr');
            if (!row) return;

            const cardId = row.id.replace('card-', '');
            
            if (e.target.classList.contains('save-card')) {
                saveCard(cardId, {
                    front: row.querySelector('[data-field="card_front"]').textContent,
                    back: row.querySelector('[data-field="card_back"]').textContent
                });
            }
            
            if (e.target.classList.contains('delete-card')) {
                if (confirm('Are you sure you want to delete this card?')) {
                    deleteCard(cardId);
                }
            }
        });
    }

    function saveCard(id, data) {
        fetch(`/revizo/edit-flashcard/${id}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(handleResponse)
        .then(() => showToast('Card updated successfully'))
        .catch(error => {
            console.error('Error:', error);
            showToast('Failed to update card', 'error');
        });
    }

    function deleteCard(id) {
        fetch(`/revizo/delete-flashcard/${id}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(handleResponse)
        .then(() => {
            document.getElementById(`card-${id}`)?.remove();
            showToast('Card deleted successfully');
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Failed to delete card', 'error');
        });
    }

    function getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]').content;
    }

    function handleResponse(response) {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
    }

    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">${message}</div>
            <div class="toast-progress"></div>
        `;
        
        document.body.appendChild(toast);
        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
});
