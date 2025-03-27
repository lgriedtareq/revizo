document.addEventListener('DOMContentLoaded', function() {
    const config = {
        urls: window.REVIZO_URLS || {
            getTopics: '/revizo/flashcards/topics/',
            filterCards: '/revizo/flashcards/filter/',
            addCard: '/revizo/flashcards/add/',
            editCard: '/revizo/flashcards/edit/',
            deleteCard: '/revizo/flashcards/delete/',
            getExplanation: '/revizo/flashcards/explanation/',
            getSuggestions: '/revizo/flashcards/suggestions/'
        }        
    };

    if (!config.urls.getTopics) {
        return;
    }
    
    // Add event listener for the "Add New Flashcard" button
    document.querySelector('[data-toggle="modal"][data-target="#addCardModal"]').addEventListener('click', function() {
        const mainSubject = document.getElementById('subject').value;
        const modalSubject = document.getElementById('modal-subject');
        const modalTopic = document.getElementById('modal-topic');
        const mainTopic = document.getElementById('topic').value;
        
        modalSubject.value = mainSubject;
        
        if (mainSubject) {
            // Fetch topics directly instead of triggering change event
            fetchTopics(mainSubject, modalTopic).then(() => {
                if (mainTopic) {
                    modalTopic.value = mainTopic;
                }
            });
        } else {
            modalTopic.innerHTML = '<option value="">-- Select Topic --</option>';
        }
    });
    
    // Helper function for custom confirmation modal
    function showCustomConfirm(message) {
        return new Promise((resolve) => {
            // Set the message in the modal
            const confirmMessageEl = document.getElementById('confirmMessage');
            confirmMessageEl.innerHTML = message;

            // Show the modal
            $('#confirmModal').modal('show');

            // Grab the buttons
            const yesBtn = document.getElementById('confirmYes');
            const noBtn = document.getElementById('confirmNo');

            // Define click handlers
            const handleYes = () => {
                cleanup();
                resolve(true);
            };

            const handleNo = () => {
                cleanup();
                resolve(false);
            };

            // Cleanup function to remove event listeners & hide modal
            function cleanup() {
                yesBtn.removeEventListener('click', handleYes);
                noBtn.removeEventListener('click', handleNo);
                $('#confirmModal').modal('hide');
            }

            // Attach event listeners
            yesBtn.addEventListener('click', handleYes);
            noBtn.addEventListener('click', handleNo);
        });
    }
    
    // Helper function for delete confirmation modal
    function showDeleteConfirm(message) {
        return new Promise((resolve) => {
            // Set the message if you want to customize it
            const messageEl = document.getElementById('confirmDeleteMessage');
            if (message) {
                messageEl.textContent = message;
            }

            // Show the modal
            $('#confirmDeleteModal').modal('show');

            // Get the buttons
            const yesBtn = document.getElementById('confirmDeleteYes');
            const noBtn = document.getElementById('confirmDeleteNo');

            // Handler for Yes
            const onYes = () => {
                cleanup();
                resolve(true);
            };

            // Handler for No
            const onNo = () => {
                cleanup();
                resolve(false);
            };

            // Remove listeners & hide modal
            function cleanup() {
                yesBtn.removeEventListener('click', onYes);
                noBtn.removeEventListener('click', onNo);
                $('#confirmDeleteModal').modal('hide');
            }

            // Attach listeners
            yesBtn.addEventListener('click', onYes);
            noBtn.addEventListener('click', onNo);
        });
    }
    
    initSubjectFilters();
    initTopicFilters();
    initCardActions();
    initModal();
    initModalSubjectFilter();

    function initSubjectFilters() {
        const subjectSelect = document.getElementById('subject');
        const topicSelect = document.getElementById('topic');
        
        subjectSelect.addEventListener('change', function() {
            const subjectId = this.value;
            
            // Always clear the topic dropdown first
            topicSelect.innerHTML = '<option value="">-- Select --</option>';
            
            if (subjectId) {
                fetchTopics(subjectId, topicSelect);
                filterCards(subjectId, null);
            } else {
                filterCards(null, null);
            }
        });

        // Only fetch initial topics if we have an initial subject selected
        // and it wasn't triggered by a change event
        const initialSubject = subjectSelect.value;
        if (initialSubject && !subjectSelect.dataset.initialized) {
            fetchTopics(initialSubject, topicSelect);
            subjectSelect.dataset.initialized = 'true';
        }
    }

    function initTopicFilters() {
        const topicSelect = document.getElementById('topic');
        
        topicSelect.addEventListener('change', function() {
            const topicId = this.value;
            const subjectId = document.getElementById('subject').value;
            filterCards(subjectId, topicId);
        });
    }

    function filterCards(subjectId, topicId) {
        let url = config.urls.filterCards;
        const params = new URLSearchParams();
        
        if (subjectId) {
            params.append('subject_id', subjectId);
        }
        if (topicId) {
            params.append('topic_id', topicId);
        }
        
        url = `${url}?${params.toString()}`;
        
        fetch(url, {
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
        .then(data => {
            updateCardTable(data.flashcards);
        })
        .catch(error => {
            showToast('Error loading cards: ' + error.message, 'error');
        });
    }

    function initModalSubjectFilter() {
        const modalSubjectSelect = document.getElementById('modal-subject');
        const modalTopicSelect = document.getElementById('modal-topic');
        
        modalSubjectSelect.addEventListener('change', function() {
            const subjectId = this.value;
            
            // Always clear the modal topic dropdown first
            modalTopicSelect.innerHTML = '<option value="">-- Select Topic --</option>';
            
            if (subjectId) {
                fetchTopics(subjectId, modalTopicSelect);
            }
        });
    }

    function initModal() {
        const modal = document.getElementById('addCardModal');
        const form = document.getElementById('addCardForm');
        
        modal.addEventListener('hidden.bs.modal', function() {
            form.reset();
            document.getElementById('modal-topic').innerHTML = '<option value="">-- Select Topic --</option>';
        });

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get the selected topic ID
            const topicId = document.getElementById('modal-topic').value;
            if (!topicId) {
                showToast('Please select a topic', 'error');
                return;
            }

            // Create FormData from the form
            const formData = new FormData(this);

            // Ensure we have all required fields
            if (!formData.get('card_front') || !formData.get('card_back')) {
                showToast('Please fill in both front and back content', 'error');
                return;
            }

            fetch(config.urls.addCard, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData,
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    return response.text().then(text => {
                        try {
                            const data = JSON.parse(text);
                            throw new Error(data.error || 'Server error');
                        } catch (e) {
                            throw new Error(text || 'Server error');
                        }
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    $('#addCardModal').modal('hide');
                    const subjectId = document.getElementById('subject').value;
                    const topicId = document.getElementById('topic').value;
                    filterCards(subjectId, topicId);
                    showToast('Card added successfully');
                    form.reset();
                } else {
                    throw new Error(data.error || 'Failed to add card');
                }
            })
            .catch(error => {
                showToast('Error adding card: ' + error.message, 'error');
                console.error('Error adding card:', error);
            });
        });
    }

    function fetchTopics(subjectId, targetSelect) {
        if (!subjectId) {
            targetSelect.innerHTML = '<option value="">-- Select Topic --</option>';
            return Promise.resolve();
        }
        
        // Clear existing options first
        targetSelect.innerHTML = '<option value="">-- Select Topic --</option>';
        
        return fetch(`${config.urls.getTopics}?subject_id=${subjectId}`, {
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
        .then(topics => {
            if (Array.isArray(topics)) {
                // Use a Set to track unique topic IDs
                const addedTopicIds = new Set();
                
                topics.forEach(topic => {
                    // Only add if we haven't seen this topic ID before
                    if (!addedTopicIds.has(topic.id)) {
                        const option = document.createElement('option');
                        option.value = topic.id;
                        option.textContent = topic.topic_name;
                        targetSelect.appendChild(option);
                        addedTopicIds.add(topic.id);
                    }
                });
            } else {
                console.error('Invalid topics data:', topics);
                targetSelect.innerHTML = '<option value="">Error loading topics</option>';
            }
        })
        .catch(error => {
            console.error('Error fetching topics:', error);
            targetSelect.innerHTML = '<option value="">Error loading topics</option>';
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
        const tbody = document.querySelector('table tbody');
        if (!tbody) {
            return;
        }
        
        tbody.addEventListener('click', function(e) {
            const row = e.target.closest('tr');
            if (!row) return;
            
            const cardId = row.id.replace('card-', '');
            
            if (e.target.classList.contains('save-card')) {
                const frontContent = row.querySelector('[data-field="card_front"]').textContent;
                const backContent = row.querySelector('[data-field="card_back"]').textContent;
                
                const url = config.urls.editCard.replace('0', cardId);
                
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({
                        front: frontContent,
                        back: backContent
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showToast('Card saved successfully');
                    } else {
                        throw new Error(data.error || 'Failed to save card');
                    }
                })
                .catch(error => {
                    showToast('Error saving card: ' + error.message, 'error');
                });
            }
            
            if (e.target.classList.contains('delete-card')) {
                e.preventDefault();
                const frontContent = row.querySelector('[data-field="card_front"]').textContent;
                const backContent = row.querySelector('[data-field="card_back"]').textContent;
                
                const confirmMessage = `Are you sure you want to delete this flashcard?\n\nFront: ${frontContent}\nBack: ${backContent}`;
                
                if (confirm(confirmMessage)) {
                    const url = config.urls.deleteCard.replace('0', cardId);
                    
                    fetch(url, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCSRFToken()
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            row.remove();
                            showToast('Card deleted successfully');
                        } else {
                            throw new Error(data.error || 'Failed to delete card');
                        }
                    })
                    .catch(error => {
                        showToast('Error deleting card: ' + error.message, 'error');
                    });
                }
            }
        });
    }

    function getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
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