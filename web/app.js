// REST API Configuration
const API_BASE_URL = 'http://localhost:5002';

// Global state
let currentUser = null;
let currentMode = '找对象';
let allUsers = [];
let allTags = [];

// Sample user data (since we're using the existing JSON profiles)
const sampleUsers = [
    {
        id: '11111111-1111-1111-1111-111111111111',
        username: 'alex_chen',
        age: 25,
        gender: 'male',
        location_city: '深圳',
        location_state: '广东',
        bio: '后端开发工程师，曾在字节跳动和美团工作。热爱技术和创新，希望找到一个理解技术人生活节奏的女生。',
        occupation: '后端开发工程师',
        looking_for: ['寻找真爱', '长期关系', '结婚生子'],
        tags: [
            { name: '内向安静', weight: 9 },
            { name: '理性冷静', weight: 8 },
            { name: '完美主义', weight: 8 },
            { name: '科技', weight: 9 },
            { name: '游戏', weight: 7 },
            { name: '运动健身', weight: 6 }
        ]
    },
    {
        id: '22222222-2222-2222-2222-222222222222',
        username: 'sophia_wang',
        age: 30,
        gender: 'female',
        location_city: '杭州',
        location_state: '浙江',
        bio: '资深UI/UX设计师，曾在腾讯和网易工作。正在筹备设计工作室，寻找技术合伙人一起做有温度的产品。',
        occupation: '资深UI/UX设计师',
        looking_for: ['产品合作', '创业伙伴'],
        tags: [
            { name: '外向开朗', weight: 8 },
            { name: '感性浪漫', weight: 7 },
            { name: '随性自由', weight: 8 },
            { name: 'UI/UX设计', weight: 9 },
            { name: '艺术', weight: 8 },
            { name: '摄影', weight: 7 }
        ]
    },
    {
        id: '33333333-3333-3333-3333-333333333333',
        username: 'kevin_li',
        age: 35,
        gender: 'male',
        location_city: '北京',
        location_state: '北京',
        bio: 'SaaS公司CEO和创始人，前阿里产品经理和麦肯锡咨询师。希望找到独立自强、有事业追求的女性。',
        occupation: 'CEO/创始人',
        looking_for: ['寻找真爱', '结婚生子', '生活伴侣'],
        tags: [
            { name: '外向开朗', weight: 9 },
            { name: '理性冷静', weight: 8 },
            { name: '独立自主', weight: 9 },
            { name: '冒险精神', weight: 8 },
            { name: '投资理财', weight: 9 }
        ]
    },
    {
        id: '44444444-4444-4444-4444-444444444444',
        username: 'luna_zhang',
        age: 30,
        gender: 'female',
        location_city: '成都',
        location_state: '四川',
        bio: '自由职业内容创作者，专注文案写作和视频制作。寻找内容创作领域的合作伙伴，一起做有创意的项目。',
        occupation: '自由职业者/内容创作者',
        looking_for: ['创意合作', '自由职业'],
        tags: [
            { name: '内向安静', weight: 7 },
            { name: '感性浪漫', weight: 8 },
            { name: '随性自由', weight: 9 },
            { name: '文案写作', weight: 9 },
            { name: '摄影', weight: 8 }
        ]
    },
    {
        id: '55555555-5555-5555-5555-555555555555',
        username: 'david_wu',
        age: 35,
        gender: 'male',
        location_city: '上海',
        location_state: '上海',
        bio: '心血管内科主治医师，曾在协和医院和约翰霍普金斯访学。希望找到善良温柔、理解医生工作的女性。',
        occupation: '心血管内科主治医师',
        looking_for: ['寻找真爱', '结婚生子', '生活伴侣', '相互支持'],
        tags: [
            { name: '内向安静', weight: 8 },
            { name: '温和体贴', weight: 9 },
            { name: '稳重踏实', weight: 9 },
            { name: '理性冷静', weight: 8 },
            { name: '古典音乐', weight: 7 }
        ]
    },
    {
        id: '66666666-6666-6666-6666-666666666666',
        username: 'iris_chen',
        age: 30,
        gender: 'female',
        location_city: '北京',
        location_state: '北京',
        bio: '独立艺术家和策展人，专注当代艺术与科技融合。寻找有技术背景但对艺术敏感的合作伙伴。',
        occupation: '独立艺术家/策展人',
        looking_for: ['艺术合作', '跨界项目'],
        tags: [
            { name: '内向安静', weight: 8 },
            { name: '感性浪漫', weight: 9 },
            { name: '独立自主', weight: 8 },
            { name: '绘画', weight: 9 },
            { name: '艺术创作', weight: 9 }
        ]
    },
    {
        id: '77777777-7777-7777-7777-777777777777',
        username: 'michael_zhang',
        age: 30,
        gender: 'male',
        location_city: '上海',
        location_state: '上海',
        bio: '投资银行副总裁，前高盛分析师。希望找到聪明独立、有自己事业的女性，一起规划未来。',
        occupation: '投资银行副总裁',
        looking_for: ['寻找真爱', '长期关系', '结婚生子', '共同成长'],
        tags: [
            { name: '外向开朗', weight: 8 },
            { name: '理性冷静', weight: 9 },
            { name: '稳重踏实', weight: 8 },
            { name: '投资理财', weight: 9 },
            { name: '高尔夫', weight: 7 }
        ]
    },
    {
        id: '88888888-8888-8888-8888-888888888888',
        username: 'jenny_liu',
        age: 25,
        gender: 'female',
        location_city: '广州',
        location_state: '广东',
        bio: '小学语文教师，专注教育创新。寻找教育科技领域的合作伙伴，希望用科技让教育更有趣、更有效。',
        occupation: '小学语文教师/教育创新者',
        looking_for: ['教育合作', '科技创新'],
        tags: [
            { name: '外向开朗', weight: 8 },
            { name: '温和体贴', weight: 9 },
            { name: '独立自主', weight: 7 },
            { name: '教学', weight: 9 },
            { name: '阅读', weight: 8 }
        ]
    },
    {
        id: '99999999-9999-9999-9999-999999999999',
        username: 'jason_wang',
        age: 30,
        gender: 'male',
        location_city: '西安',
        location_state: '陕西',
        bio: '健身教练和运动康复师，前职业篮球运动员。希望找到积极阳光、热爱生活的女生，一起过健康快乐的生活。',
        occupation: '健身教练/运动康复师',
        looking_for: ['寻找真爱', '长期关系', '共同成长', '浪漫恋爱'],
        tags: [
            { name: '外向开朗', weight: 9 },
            { name: '幽默风趣', weight: 8 },
            { name: '冒险精神', weight: 8 },
            { name: '运动健身', weight: 9 },
            { name: '篮球', weight: 9 }
        ]
    },
    {
        id: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
        username: 'alice_zhou',
        age: 30,
        gender: 'female',
        location_city: '深圳',
        location_state: '广东',
        bio: 'AI研究员，清华博士。希望将AI研究成果转化为实际应用，寻找有技术实力和商业敏感度的合作伙伴。',
        occupation: '人工智能研究员',
        looking_for: ['技术合作', '产品转化'],
        tags: [
            { name: '内向安静', weight: 8 },
            { name: '理性冷静', weight: 9 },
            { name: '独立自主', weight: 9 },
            { name: '科技', weight: 9 },
            { name: '机器学习', weight: 9 }
        ]
    }
];

// DOM Elements
const loginSection = document.getElementById('loginSection');
const appSection = document.getElementById('appSection');
const userInfo = document.getElementById('userInfo');
const tabButtons = document.querySelectorAll('.tab-button');
const searchTitle = document.getElementById('searchTitle');
const queryInput = document.getElementById('queryInput');
const searchBtn = document.getElementById('searchBtn');
const resultsCount = document.getElementById('resultsCount');
const resultsBody = document.getElementById('resultsBody');
const noResults = document.getElementById('noResults');
const loadingOverlay = document.getElementById('loadingOverlay');

// API helper functions
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.message || `HTTP ${response.status}`);
        }
        
        return result;
    } catch (error) {
        console.error(`API call failed for ${endpoint}:`, error);
        throw error;
    }
}

// Initialize the application
async function initApp() {
    try {
        console.log('Initializing app...');
        
        // Check API health
        await checkApiHealth();
        
        // Load data
        await loadUsers();
        await loadTags();
        
        // Login as Alex Chen
        await loginAsAlexChen();
        
        // Setup event listeners
        setupEventListeners();
        
        // Show initial results
        await performSearch('');
        
    } catch (error) {
        console.error('Failed to initialize app:', error);
        showError('应用初始化失败，请确保API服务器运行正常');
    }
}

// Check API server health
async function checkApiHealth() {
    try {
        const result = await apiCall('/health');
        console.log('API Health:', result.message);
        return true;
    } catch (error) {
        throw new Error('API服务器无法连接，请确保在端口5000上运行api_server.py');
    }
}

// Load users data
async function loadUsers() {
    try {
        const result = await apiCall('/api/database/users');
        if (result.success) {
            allUsers = result.data || [];
            console.log('Loaded users from database:', allUsers.length);
        } else {
            throw new Error(result.message || 'Failed to load users');
        }
    } catch (error) {
        console.error('Error loading users from database:', error);
        console.log('Falling back to sample data...');
        // Fallback to sample data if API fails
        allUsers = sampleUsers;
    }
}

// Load tags data
async function loadTags() {
    try {
        const result = await apiCall('/api/database/tags');
        if (result.success) {
            allTags = result.data.all_tags || [];
            console.log('Loaded tags from database:', allTags.length);
        } else {
            throw new Error(result.message || 'Failed to load tags');
        }
    } catch (error) {
        console.error('Error loading tags from database:', error);
        // Continue without tags if API fails
        allTags = [];
    }
}

// Login as Alex Chen
async function loginAsAlexChen() {
    try {
        currentUser = allUsers.find(user => user.username === 'alex_chen');
        if (!currentUser) {
            throw new Error('Alex Chen user not found');
        }
        
        // Update UI
        showUserProfile();
        showAppSection();
        
        console.log('Logged in as:', currentUser.username);
    } catch (error) {
        console.error('Login failed:', error);
        throw error;
    }
}

// Show user profile in header
function showUserProfile() {
    const userProfile = `
        <div class="user-profile">
            <div class="user-avatar">${currentUser.username.charAt(0).toUpperCase()}</div>
            <div class="user-details">
                <h4>${currentUser.username}</h4>
                <p>${currentUser.occupation || '程序员'}</p>
            </div>
        </div>
    `;
    userInfo.innerHTML = userProfile;
}

// Show main app section
function showAppSection() {
    loginSection.style.display = 'none';
    appSection.style.display = 'block';
}

// Setup event listeners
function setupEventListeners() {
    // Tab switching
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const mode = button.dataset.mode;
            switchMode(mode);
        });
    });
    
    // Search functionality
    searchBtn.addEventListener('click', handleSearch);
    queryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSearch();
        }
    });
}

// Switch between modes
function switchMode(mode) {
    currentMode = mode;
    
    // Update tab buttons
    tabButtons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });
    
    // Update search title and placeholder
    if (mode === '找对象') {
        searchTitle.textContent = '寻找理想的另一半';
        queryInput.placeholder = '例如：希望找到一个理解技术人生活节奏的女生，年龄23-28岁，最好也在深圳...';
    } else {
        searchTitle.textContent = '寻找合作伙伴';
        queryInput.placeholder = '例如：寻找有技术背景但对艺术敏感的合作伙伴，一起做有创意的项目...';
    }
    
    // Perform new search
    performSearch(queryInput.value);
}

// Handle search button click
async function handleSearch() {
    console.log('开始匹配按钮被点击');
    const query = queryInput.value.trim();
    console.log('搜索查询:', query);
    
    // 防止重复点击
    if (searchBtn.disabled) {
        console.log('搜索正在进行中，忽略重复点击');
        return;
    }
    
    try {
        await performSearch(query);
    } catch (error) {
        console.error('搜索失败:', error);
        showError('匹配失败: ' + error.message);
    }
}

// Perform search and display results
async function performSearch(query) {
    console.log('开始执行搜索，查询:', query);
    try {
        showLoading(true);
        console.log('Loading状态已开启');
        
        // Filter users based on mode
        let filteredUsers = filterUsersByMode();
        console.log(`基于模式${currentMode}筛选后的用户数量:`, filteredUsers.length);
        
        if (query) {
            filteredUsers = filterUsersByQuery(filteredUsers, query);
            console.log('基于查询筛选后的用户数量:', filteredUsers.length);
        }
        
        // For each filtered user, calculate match score using API
        const resultsWithScores = [];
        console.log('开始计算匹配分数...');
        
        for (let i = 0; i < filteredUsers.length; i++) {
            const user = filteredUsers[i];
            console.log(`正在处理用户 ${i + 1}/${filteredUsers.length}: ${user.username}`);
            
            try {
                const matchScore = await calculateMatchScore(currentUser, user, query);
                resultsWithScores.push({
                    ...user,
                    matchScore: matchScore,
                    matchFactors: getMatchFactors(currentUser, user)
                });
                console.log(`${user.username} 匹配分数: ${matchScore}%`);
            } catch (error) {
                console.warn(`Failed to calculate match for ${user.username}:`, error);
                // Fallback to simple scoring
                const simpleScore = calculateSimpleMatchScore(currentUser, user, query);
                resultsWithScores.push({
                    ...user,
                    matchScore: simpleScore,
                    matchFactors: getMatchFactors(currentUser, user)
                });
                console.log(`${user.username} 使用简单算法分数: ${simpleScore}%`);
            }
        }
        
        // Sort by match score
        resultsWithScores.sort((a, b) => b.matchScore - a.matchScore);
        console.log('匹配结果排序完成，总数:', resultsWithScores.length);
        
        // Display results
        displayResults(resultsWithScores);
        console.log('结果已显示');
        
    } catch (error) {
        console.error('Search failed:', error);
        showError('搜索失败: ' + error.message);
        // 显示空结果而不是完全失败
        displayResults([]);
    } finally {
        showLoading(false);
        console.log('Loading状态已关闭');
    }
}

// Calculate match score using LDA API
async function calculateMatchScore(userA, userB, query) {
    try {
        // Use the new LDA-based matching API
        const result = await apiCall('/api/match/lda', 'POST', {
            query: query || '',
            current_user: userA,
            candidate_user: userB,
            mode: currentMode
        });
        
        if (result.success && result.data && result.data.match_score !== undefined) {
            // Convert LDA score (0-1) to percentage (0-100)
            return Math.round(result.data.match_score * 100);
        }
        
        return 50; // Fallback score
    } catch (error) {
        console.warn('LDA matching failed, using simple scoring:', error);
        return calculateSimpleMatchScore(userA, userB, query);
    }
}

// Convert user data to API expected format
function convertToApiFormat(user, query = '') {
    return {
        profile: {
            name: {
                display_name: user.username,
                nickname: user.username
            },
            personal: {
                age_range: `${user.age}岁`,
                location: user.location_city,
                bio: user.bio
            },
            professional: {
                current_role: user.occupation
            },
            personality: {
                personality_traits: user.tags ? user.tags.map(tag => tag.name) : [],
                interests: user.tags ? user.tags.map(tag => tag.name) : []
            }
        },
        user_request: {
            request_type: currentMode,
            description: query || user.bio
        }
    };
}

// Simple fallback match scoring
function calculateSimpleMatchScore(userA, userB, query) {
    let score = 50; // Base score
    
    // Location bonus
    if (userA.location_city === userB.location_city) {
        score += 20;
    } else if (userA.location_state === userB.location_state) {
        score += 10;
    }
    
    // Age compatibility
    const ageDiff = Math.abs(userA.age - userB.age);
    if (ageDiff <= 2) {
        score += 15;
    } else if (ageDiff <= 5) {
        score += 10;
    }
    
    // Tag similarity
    if (userA.tags && userB.tags) {
        const commonTags = getCommonTags(userA.tags, userB.tags);
        score += Math.min(commonTags.length * 5, 15);
    }
    
    return Math.min(score, 100);
}

// Filter users by current mode
function filterUsersByMode() {
    // Exclude current user
    let filtered = allUsers.filter(user => user.id !== currentUser.id);
    
    console.log(`原始用户数量 (排除当前用户): ${filtered.length}`);
    
    if (currentMode === '找对象') {
        // For dating: filter by gender only (more flexible approach)
        filtered = filtered.filter(user => {
            // Basic gender filtering for heterosexual matching
            if (currentUser.gender === 'male' && user.gender !== 'female') return false;
            if (currentUser.gender === 'female' && user.gender !== 'male') return false;
            
            // More flexible goal matching - include users who might be open to dating
            const datingGoals = ['寻找真爱', '长期关系', '结婚生子', '浪漫恋爱', '生活伴侣', '共同成长'];
            const userGoals = user.looking_for || [];
            
            // If user has dating goals, include them
            if (userGoals.some(goal => datingGoals.includes(goal))) {
                return true;
            }
            
            // If user has no specific dating goals but has collaborative goals, 
            // still include them as potential matches (they might be open to dating)
            const collaborativeGoals = ['产品合作', '创业伙伴', '技术合作', '创意合作', '艺术合作', '教育合作'];
            return userGoals.some(goal => collaborativeGoals.includes(goal));
        });
    } else {
        // For teamwork: filter by collaboration goals
        filtered = filtered.filter(user => {
            const teamGoals = ['找队友', '产品合作', '创业伙伴', '技术合作', '创意合作', '艺术合作', '教育合作', '科技创新', '产品转化', '跨界项目', '自由职业'];
            const userGoals = user.looking_for || [];
            return userGoals.some(goal => teamGoals.includes(goal));
        });
    }
    
    console.log(`模式 ${currentMode} 筛选后用户数量: ${filtered.length}`);
    console.log('筛选后的用户:', filtered.map(u => u.username));
    
    return filtered;
}

// Filter users by search query
function filterUsersByQuery(users, query) {
    if (!query) return users;
    
    const queryLower = query.toLowerCase();
    
    return users.filter(user => {
        const searchFields = [
            user.bio || '',
            user.occupation || '',
            user.location_city || '',
            user.location_state || '',
            ...(user.looking_for || []),
            ...(user.tags || []).map(tag => tag.name)
        ].join(' ').toLowerCase();
        
        const queryTerms = queryLower.split(/\s+/);
        return queryTerms.some(term => searchFields.includes(term));
    });
}

// Get common tags between two users
function getCommonTags(tags1, tags2) {
    const tagNames1 = tags1.map(t => t.name);
    return tags2.filter(tag => tagNames1.includes(tag.name));
}

// Get match factors for display
function getMatchFactors(userA, userB) {
    const factors = [];
    
    if (userA.location_city === userB.location_city) {
        factors.push('同城');
    } else if (userA.location_state === userB.location_state) {
        factors.push('同省');
    }
    
    const ageDiff = Math.abs(userA.age - userB.age);
    if (ageDiff <= 2) {
        factors.push('年龄匹配');
    }
    
    if (userA.tags && userB.tags) {
        const commonTags = getCommonTags(userA.tags, userB.tags);
        if (commonTags.length > 0) {
            factors.push(`共同标签: ${commonTags.slice(0, 3).map(t => t.name).join(', ')}`);
        }
    }
    
    return factors;
}

// Display search results
function displayResults(results) {
    resultsCount.textContent = `${results.length} 个匹配`;
    
    if (results.length === 0) {
        document.getElementById('resultsTable').style.display = 'none';
        noResults.style.display = 'block';
        return;
    }
    
    document.getElementById('resultsTable').style.display = 'table';
    noResults.style.display = 'none';
    
    resultsBody.innerHTML = results.map(user => `
        <tr>
            <td>
                <div class="user-avatar-small">${user.username.charAt(0).toUpperCase()}</div>
            </td>
            <td><strong>${user.username}</strong></td>
            <td>${user.age || '未知'}</td>
            <td>${getGenderText(user.gender)}</td>
            <td>${user.location_city || '未知'}</td>
            <td>${user.occupation || '未知'}</td>
            <td>
                <div class="tags-container">
                    ${(user.tags || []).slice(0, 3).map(tag => `
                        <span class="tag">${tag.name}</span>
                    `).join('')}
                    ${(user.tags || []).length > 3 ? `<span class="tag">+${(user.tags || []).length - 3}</span>` : ''}
                </div>
            </td>
            <td>
                <div class="match-score ${getScoreClass(user.matchScore)}">
                    ${user.matchScore}%
                </div>
            </td>
            <td>
                <button class="action-btn primary" onclick="viewProfile('${user.id}')">
                    查看
                </button>
            </td>
        </tr>
    `).join('');
}

// Helper functions
function getGenderText(gender) {
    const genderMap = {
        'male': '男',
        'female': '女',
        'non-binary': '其他',
        'other': '其他',
        'prefer-not-to-say': '保密'
    };
    return genderMap[gender] || '未知';
}

function getScoreClass(score) {
    if (score >= 80) return 'high';
    if (score >= 60) return 'medium';
    return 'low';
}

function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
    console.log('Loading显示状态:', show ? '显示' : '隐藏');
    
    // 同时更新搜索按钮状态
    if (show) {
        searchBtn.classList.add('loading');
        searchBtn.innerHTML = '<div class="loading-spinner small"></div> 匹配中...';
    } else {
        searchBtn.classList.remove('loading');
        searchBtn.innerHTML = '🔍 开始匹配';
    }
}

function showError(message) {
    console.error('显示错误消息:', message);
    
    // 创建更友好的错误提示
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-toast';
    errorDiv.innerHTML = `
        <div class="error-content">
            <span class="error-icon">⚠️</span>
            <span class="error-message">${message}</span>
            <button class="error-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    document.body.appendChild(errorDiv);
    
    // 自动移除错误提示
    setTimeout(() => {
        if (errorDiv.parentElement) {
            errorDiv.remove();
        }
    }, 5000);
}

// View user profile
function viewProfile(userId) {
    const user = allUsers.find(u => u.id === userId);
    if (user) {
        alert(`查看 ${user.username} 的详细资料\n\n年龄: ${user.age}\n职业: ${user.occupation}\n城市: ${user.location_city}\n\n${user.bio || '暂无简介'}`);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', initApp);

// Export for debugging
window.appDebug = {
    currentUser,
    allUsers,
    allTags,
    apiCall,
    calculateMatchScore
}; 