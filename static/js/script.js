// 游戏状态管理
let gameState = {
    gameId: null,
    attempts: 0,
    maxAttempts: 6,
    gameOver: false,
    won: false,
    guessHistory: []
};

// DOM 元素
const elements = {
    rules: document.getElementById('rules'),
    gameGrid: document.getElementById('gameGrid'),
    inputArea: document.getElementById('inputArea'),
    gameResult: document.getElementById('gameResult'),
    loading: document.getElementById('loading'),
    toast: document.getElementById('toast'),
    
    guessHistory: document.getElementById('guessHistory'),
    currentGuess: document.getElementById('currentGuess'),
    wordInput: document.getElementById('wordInput'),
    attemptInfo: document.getElementById('attemptInfo'),
    
    resultTitle: document.getElementById('resultTitle'),
    resultMessage: document.getElementById('resultMessage'),
    answerDetails: document.getElementById('answerDetails'),
    answerGrid: document.getElementById('answerGrid'),
    toastMessage: document.getElementById('toastMessage')
};

// API 调用函数
async function apiCall(url, method = 'GET', data = null) {
    try {
        showLoading();
        
        const config = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            config.body = JSON.stringify(data);
        }
        
        const response = await fetch(url, config);
        const result = await response.json();
        
        return result;
    } catch (error) {
        console.error('API调用错误:', error);
        showToast('网络错误，请重试');
        return { success: false, message: '网络错误' };
    } finally {
        hideLoading();
    }
}

// 开始新游戏
async function startNewGame() {
    const result = await apiCall('/api/new_game', 'POST');
    
    if (result.success) {
        gameState.gameId = result.game_id;
        gameState.maxAttempts = result.max_attempts;
        gameState.attempts = 0;
        gameState.gameOver = false;
        gameState.won = false;
        gameState.guessHistory = [];
        
        showGameGrid();
        updateAttemptInfo();
        clearGuessHistory();
        clearCurrentGuess();
        elements.wordInput.focus();
    } else {
        showToast(result.message || '开始游戏失败');
    }
}

// 提交猜测
async function submitGuess() {
    const word = elements.wordInput.value.trim();
    
    if (!word) {
        showToast('请输入词语');
        return;
    }
    
    if (word.length !== 4) {
        showToast('请输入四个字的词语');
        return;
    }
    
    // 检查是否只包含中文字符
    const chineseOnly = word.replace(/[^\u4e00-\u9fa5]/g, '');
    if (word !== chineseOnly) {
        showToast('请只输入中文字符');
        return;
    }
    
    const result = await apiCall('/api/guess', 'POST', { word: word });
    
    if (result.success) {
        addGuessToHistory(word, result.result);
        gameState.attempts = result.attempts;
        updateAttemptInfo();
        
        if (result.game_over) {
            gameState.gameOver = true;
            gameState.won = result.won;
            showGameResult(result);
        } else {
            elements.wordInput.value = '';
            elements.wordInput.focus();
        }
    } else {
        showToast(result.message || '提交失败');
    }
}

// 显示游戏网格
function showGameGrid() {
    elements.rules.style.display = 'none';
    elements.gameGrid.style.display = 'flex';
    elements.inputArea.style.display = 'block';
    elements.gameResult.style.display = 'none';
}

// 显示游戏结果
function showGameResult(result) {
    elements.inputArea.style.display = 'none';
    elements.gameResult.style.display = 'block';
    
    if (result.won) {
        elements.resultTitle.textContent = '🎉 恭喜获胜！';
        elements.resultTitle.style.color = '#6aaa64';
    } else {
        elements.resultTitle.textContent = '😞 游戏结束';
        elements.resultTitle.style.color = '#787c7e';
    }
    
    elements.resultMessage.textContent = result.message;
    
    if (!result.won && result.target_details) {
        elements.answerDetails.style.display = 'block';
        showAnswerDetails(result.target_details);
    } else {
        elements.answerDetails.style.display = 'none';
    }
}

// 显示答案详情
function showAnswerDetails(targetDetails) {
    elements.answerGrid.innerHTML = '';
    
    targetDetails.forEach(charInfo => {
        const charBlock = createCharBlock(charInfo.chinese, charInfo.pinyin, charInfo.tone);
        charBlock.classList.add('correct');
        elements.answerGrid.appendChild(charBlock);
    });
}

// 添加猜测到历史记录
function addGuessToHistory(word, result) {
    const guessRow = document.createElement('div');
    guessRow.className = 'guess-row new';
    
    result.forEach((charResult, index) => {
        const charBlock = createCharBlock(
            charResult.chinese.char,
            charResult.pinyin.text,
            charResult.tone.text
        );
        
        // 设置字符颜色
        setCharBlockColor(charBlock, charResult, index);
        
        guessRow.appendChild(charBlock);
    });
    
    elements.guessHistory.appendChild(guessRow);
    
    // 触发动画
    setTimeout(() => {
        guessRow.classList.remove('new');
    }, 100);
}

// 创建字符块
function createCharBlock(chinese, pinyin, tone) {
    const charBlock = document.createElement('div');
    charBlock.className = 'char-block filled';
    
    const charDiv = document.createElement('div');
    charDiv.className = 'char';
    charDiv.textContent = chinese;
    
    const pinyinDiv = document.createElement('div');
    pinyinDiv.className = 'pinyin';
    pinyinDiv.textContent = pinyin;
    
    const toneDiv = document.createElement('div');
    toneDiv.className = 'tone';
    toneDiv.textContent = tone ? `${tone}声` : '';
    
    charBlock.appendChild(charDiv);
    charBlock.appendChild(pinyinDiv);
    charBlock.appendChild(toneDiv);
    
    return charBlock;
}

// 设置字符块颜色
function setCharBlockColor(charBlock, charResult, index) {
    // 设置中文字符颜色
    const chineseColor = charResult.chinese.color;
    if (chineseColor === 'green') {
        charBlock.classList.add('correct');
    } else if (chineseColor === 'yellow') {
        charBlock.classList.add('present');
    } else {
        charBlock.classList.add('absent');
    }
    
    // 设置拼音字符颜色
    const pinyinDiv = charBlock.querySelector('.pinyin');
    const pinyinColors = charResult.pinyin.colors;
    if (pinyinColors && pinyinColors.length > 0) {
        // 如果所有字母都是同一颜色，则整体设置
        const uniqueColors = [...new Set(pinyinColors)];
        if (uniqueColors.length === 1) {
            const color = uniqueColors[0];
            if (color === 'green') {
                pinyinDiv.style.color = '#6aaa64';
            } else if (color === 'yellow') {
                pinyinDiv.style.color = '#c9b458';
            } else {
                pinyinDiv.style.color = '#787c7e';
            }
        } else {
            // 如果颜色不同，创建混合颜色显示
            let html = '';
            const pinyin = charResult.pinyin.text;
            for (let i = 0; i < pinyin.length; i++) {
                const letter = pinyin[i];
                const color = pinyinColors[i] || 'gray';
                let colorCode;
                if (color === 'green') colorCode = '#6aaa64';
                else if (color === 'yellow') colorCode = '#c9b458';
                else colorCode = '#787c7e';
                
                html += `<span style="color: ${colorCode}">${letter}</span>`;
            }
            pinyinDiv.innerHTML = html;
        }
    }
    
    // 设置声调颜色
    const toneDiv = charBlock.querySelector('.tone');
    const toneColors = charResult.tone.colors;
    if (toneColors && toneColors.length > 0) {
        const color = toneColors[0];
        if (color === 'green') {
            toneDiv.style.color = '#6aaa64';
        } else if (color === 'yellow') {
            toneDiv.style.color = '#c9b458';
        } else {
            toneDiv.style.color = '#787c7e';
        }
    }
}

// 更新尝试信息
function updateAttemptInfo() {
    elements.attemptInfo.textContent = `第 ${gameState.attempts + 1} 次 / 共 ${gameState.maxAttempts} 次`;
}

// 清空猜测历史
function clearGuessHistory() {
    elements.guessHistory.innerHTML = '';
}

// 清空当前猜测
function clearCurrentGuess() {
    const charBlocks = elements.currentGuess.querySelectorAll('.char-block');
    charBlocks.forEach(block => {
        block.querySelector('.char').textContent = '?';
        block.querySelector('.pinyin').textContent = '?';
        block.querySelector('.tone').textContent = '?';
        block.className = 'char-block';
    });
}

// 新游戏
function newGame() {
    elements.gameResult.style.display = 'none';
    elements.rules.style.display = 'block';
    elements.gameGrid.style.display = 'none';
    elements.inputArea.style.display = 'none';
}

// 显示加载状态
function showLoading() {
    elements.loading.style.display = 'flex';
}

// 隐藏加载状态
function hideLoading() {
    elements.loading.style.display = 'none';
}

// 显示提示信息
function showToast(message) {
    elements.toastMessage.textContent = message;
    elements.toast.classList.add('show');
    
    setTimeout(() => {
        hideToast();
    }, 3000);
}

// 隐藏提示信息
function hideToast() {
    elements.toast.classList.remove('show');
}

// 事件监听器
document.addEventListener('DOMContentLoaded', function() {
    // 输入框回车提交
    elements.wordInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            submitGuess();
        }
    });
    
    // 输入框实时更新当前猜测显示
    elements.wordInput.addEventListener('input', function(e) {
        const value = e.target.value;
        const charBlocks = elements.currentGuess.querySelectorAll('.char-block');
        
        // 清空所有块
        charBlocks.forEach((block, index) => {
            const char = value[index] || '?';
            block.querySelector('.char').textContent = char;
            block.querySelector('.pinyin').textContent = char === '?' ? '?' : '...';
            block.querySelector('.tone').textContent = char === '?' ? '?' : '...';
            
            if (char !== '?') {
                block.classList.add('filled');
            } else {
                block.classList.remove('filled');
            }
        });
        
        // 如果输入了4个字符，异步获取拼音和声调
        if (value.length === 4) {
            updateCurrentGuessInfo(value);
        }
    });
    
    // 输入字数限制（移除中文字符限制，允许输入法正常工作）
    elements.wordInput.addEventListener('input', function(e) {
        const value = e.target.value;
        // 只限制最大长度，不限制字符类型（支持输入法）
        if (value.length > 4) {
            e.target.value = value.substring(0, 4);
        }
    });
});

// 更新当前猜测的拼音和声调信息
async function updateCurrentGuessInfo(word) {
    try {
        // 模拟获取拼音和声调（实际应用中可能需要调用API）
        const charBlocks = elements.currentGuess.querySelectorAll('.char-block');
        
        for (let i = 0; i < word.length; i++) {
            const char = word[i];
            const block = charBlocks[i];
            
            // 这里简化处理，实际应用中应该调用后端API获取准确的拼音和声调
            block.querySelector('.pinyin').textContent = '获取中...';
            block.querySelector('.tone').textContent = '获取中...';
        }
        
        // 延迟一下模拟网络请求
        setTimeout(() => {
            charBlocks.forEach(block => {
                block.querySelector('.pinyin').textContent = '准备中';
                block.querySelector('.tone').textContent = '准备中';
            });
        }, 200);
        
    } catch (error) {
        console.error('获取拼音信息失败:', error);
    }
}

// 全局函数，供HTML调用
window.startNewGame = startNewGame;
window.submitGuess = submitGuess;
window.newGame = newGame;
window.hideToast = hideToast;