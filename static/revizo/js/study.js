document.addEventListener('DOMContentLoaded', function() {
    const config = {
        urls: window.REVIZO_URLS || {
            getExplanation: '/revizo/flashcards/explanation/',
            updateConfidence: '/revizo/flashcards/confidence/',
            getRelatedCards: '/revizo/flashcards/suggestions/'
        }
    };

    if (!config.urls.getExplanation) {
        return;
    }

    initStudySession();
    initKeyboardShortcuts();

    function initStudySession() {
        const cards = window.INITIAL_CARDS;
        if (!cards || cards.length === 0) {
            showToast('No cards available for study', 'error');
            return;
        }

        let currentCardIndex = 0;
        let isFlipped = false;
        const cardElement = document.getElementById('flashcard');
        const frontElement = document.getElementById('card-front');
        const backElement = document.getElementById('card-back');
        const nextBtn = document.getElementById('next-btn');
        const prevBtn = document.getElementById('prev-btn');
        const flipBtn = document.getElementById('flip-btn');
        const aiExplainBtn = document.getElementById('ai-explain-button');
        const confidenceBtns = document.querySelectorAll('.confidence-btn');
        const subjectTopicSpan = document.getElementById('subject-topic');
        const loadingSpinner = document.querySelector('.loading-spinner');
        const aiExplanationContainer = document.querySelector('.ai-explanation-container');
        const aiExplanationContent = document.getElementById('ai-explanation-content');
        const modalCardFront = document.getElementById('modal-card-front');
        const modalCardBack = document.getElementById('modal-card-back');

        // Set initial subject and topic
        if (cards.length > 0) {
            subjectTopicSpan.textContent = `${cards[0].subject_name} - ${cards[0].topic_name}`;
        }

        function displayCard(index) {
            if (index >= 0 && index < cards.length) {
                const card = cards[index];
                frontElement.textContent = card.card_front;
                backElement.textContent = card.card_back;
                cardElement.classList.remove('flipped');
                isFlipped = false;
                
                // Update navigation buttons
                nextBtn.disabled = false;
                prevBtn.disabled = index === 0;
                
                aiExplainBtn.disabled = false;
                aiExplanationContent.textContent = '';
            }
        }

        function flipCard() {
            if (currentCardIndex >= 0 && currentCardIndex < cards.length) {
                cardElement.classList.toggle('flipped');
                isFlipped = !isFlipped;
            }
        }

        function nextCard() {
            if (currentCardIndex < cards.length - 1) {
                currentCardIndex++;
                isFlipped = false;
                displayCard(currentCardIndex);
            } else {
                $('#lastCardModal').modal('show');
            }
        }

        function previousCard() {
            if (currentCardIndex > 0) {
                currentCardIndex--;
                isFlipped = false;
                displayCard(currentCardIndex);
            }
        }

        function getCardExplanation() {
            const card = cards[currentCardIndex];
            const loadingSpinner = document.querySelector('.loading-spinner');
            const aiExplanationContainer = document.querySelector('.ai-explanation-container');
            const aiExplanationContent = document.getElementById('ai-explanation-content');
            const modalCardFront = document.getElementById('modal-card-front');
            const modalCardBack = document.getElementById('modal-card-back');
            
            // Show loading state
            loadingSpinner.style.display = 'block';
            aiExplanationContainer.style.display = 'none';
            aiExplanationContent.textContent = '';
            
            // Display card content in modal
            modalCardFront.textContent = card.card_front;
            modalCardBack.textContent = card.card_back;
            
            // Show modal
            $('#aiExplanationModal').modal('show');
            
            const url = config.urls.getExplanation + '/' + card.id;
            
            fetch(url, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': window.CSRF_TOKEN
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                loadingSpinner.style.display = 'none';
                aiExplanationContainer.style.display = 'block';
                
                if (data.success && data.explanation) {
                    // Format the explanation text with paragraphs
                    const formattedExplanation = data.explanation
                        .split('\n')
                        .filter(line => line.trim() !== '')
                        .map(line => `<p>${line}</p>`)
                        .join('');
                    
                    aiExplanationContent.innerHTML = formattedExplanation;
                } else {
                    throw new Error(data.error || 'Failed to get explanation');
                }
            })
            .catch(error => {
                loadingSpinner.style.display = 'none';
                aiExplanationContainer.style.display = 'block';
                aiExplanationContent.innerHTML = `<div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle"></i> 
                    Error getting explanation: ${error.message}
                </div>`;
            });
        }

        function updateConfidence(level) {
            const card = cards[currentCardIndex];
            const url = config.urls.updateConfidence.replace('0', card.id);
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.CSRF_TOKEN
                },
                body: JSON.stringify({
                    confidence_level: level
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    $('#confidenceUpdateModal').modal('show');
                    // Refresh the suggested topics table if we're on the home page
                    if (window.location.pathname === '/revizo/') {
                        window.location.reload();
                    }
                    nextCard();
                } else {
                    throw new Error(data.error || 'Failed to update confidence');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Error updating confidence: ' + error.message, 'error');
            });
        }

        function getRelatedCards() {
            const card = cards[currentCardIndex];
            fetch(config.urls.getRelatedCards, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    content: card.card_front + ' ' + card.card_back
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.suggestions) {
                    const suggestionsHtml = data.suggestions
                        .map(suggestion => `<div class="suggestion-item">${suggestion}</div>`)
                        .join('');
                    showSuggestionsModal(suggestionsHtml);
                } else {
                    throw new Error(data.error || 'Failed to get suggestions');
                }
            })
            .catch(error => {
                showToast('Error getting suggestions: ' + error.message, 'error');
            });
        }

        function showSuggestionsModal(suggestionsHtml) {
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.id = 'suggestionsModal';
            modal.innerHTML = `
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Related Flashcard Suggestions</h5>
                            <button type="button" class="close" data-dismiss="modal">&times;</button>
                        </div>
                        <div class="modal-body">
                            ${suggestionsHtml}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            $('#suggestionsModal').modal('show');
            $('#suggestionsModal').on('hidden.bs.modal', function() {
                this.remove();
            });
        }

        // Event listeners
        cardElement.addEventListener('click', flipCard);
        flipBtn.addEventListener('click', flipCard);
        nextBtn.addEventListener('click', nextCard);
        prevBtn.addEventListener('click', previousCard);
        aiExplainBtn.addEventListener('click', getCardExplanation);
        
        confidenceBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const level = parseInt(btn.dataset.level);
                updateConfidence(level);
            });
        });

        // Display first card
        displayCard(0);
    }

    function initKeyboardShortcuts() {
        document.addEventListener('keydown', function(event) {
            if (event.code === 'Space') {
                event.preventDefault();
                document.getElementById('flip-btn').click();
            } else if (event.code === 'ArrowRight') {
                document.getElementById('next-btn').click();
            } else if (event.code === 'ArrowLeft') {
                document.getElementById('prev-btn').click();
            } else if (event.code === 'KeyE') {
                document.getElementById('ai-explain-button').click();
            } else if (event.code === 'Digit1') {
                document.querySelector('.confidence-btn[data-level="1"]').click();
            } else if (event.code === 'Digit2') {
                document.querySelector('.confidence-btn[data-level="2"]').click();
            } else if (event.code === 'Digit3') {
                document.querySelector('.confidence-btn[data-level="3"]').click();
            }
        });
    }

    function getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    }

    function showToast(message, type = 'info') {
        // You can implement a toast notification system here
        alert(message); // Simple fallback
    }
}); 
