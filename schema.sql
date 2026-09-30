-- =====================================================
-- CyberSafe DB Schema
-- Cybercrime Reporting and Awareness Portal
-- MySQL 5.7+ / MariaDB 10.4+ (XAMPP)
-- =====================================================

CREATE DATABASE IF NOT EXISTS cybersafe_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE cybersafe_db;

-- 1. Users
CREATE TABLE IF NOT EXISTS users (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    username     VARCHAR(50)  NOT NULL UNIQUE,
    email        VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name    VARCHAR(100) DEFAULT '',
    phone        VARCHAR(20)  DEFAULT '',
    is_admin     TINYINT(1)   DEFAULT 0,
    created_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Complaints
CREATE TABLE IF NOT EXISTS complaints (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id    VARCHAR(20) NOT NULL UNIQUE,
    user_id         INT         NOT NULL,
    incident_type   VARCHAR(80) NOT NULL,
    incident_date   DATE        NOT NULL,
    description     TEXT        NOT NULL,
    contact_name    VARCHAR(100) DEFAULT '',
    contact_email   VARCHAR(120) DEFAULT '',
    contact_phone   VARCHAR(20)  DEFAULT '',
    evidence_file   VARCHAR(255) DEFAULT NULL,
    status          ENUM('Submitted','Under Review','Resolved','Rejected') DEFAULT 'Submitted',
    admin_notes     TEXT         DEFAULT NULL,
    created_at      TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP   DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Status History
CREATE TABLE IF NOT EXISTS complaint_history (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id VARCHAR(20) NOT NULL,
    old_status   VARCHAR(50) DEFAULT NULL,
    new_status   VARCHAR(50) NOT NULL,
    notes        TEXT        DEFAULT NULL,
    changed_by   INT         DEFAULT NULL,
    changed_at   TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by)   REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Awareness Articles
CREATE TABLE IF NOT EXISTS articles (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    title        VARCHAR(200) NOT NULL,
    category     VARCHAR(80)  NOT NULL,
    summary      VARCHAR(400) NOT NULL,
    content      TEXT         NOT NULL,
    icon         VARCHAR(60)  DEFAULT 'shield',
    is_published TINYINT(1)   DEFAULT 1,
    author_id    INT          DEFAULT NULL,
    created_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ─────────────────────────────
-- Default Accounts
-- admin / Admin@123
-- user1 / User@1234
-- ─────────────────────────────
INSERT INTO users (username, email, password_hash, full_name, is_admin)
VALUES
('admin',
 'admin@cybersafe.local',
 'scrypt:32768:8:1$cybersafe2026salt$placeholder_admin_hash',
 'CyberSafe Administrator',
 1),
('user1',
 'user1@cybersafe.local',
 'scrypt:32768:8:1$cybersafe2026salt$placeholder_user_hash',
 'Demo User',
 0)
ON DUPLICATE KEY UPDATE id=id;

-- ─────────────────────────────
-- Seed Awareness Articles
-- ─────────────────────────────
INSERT INTO articles (title, category, summary, content, icon, author_id)
SELECT * FROM (SELECT
  'How to Recognise a Phishing Email' AS title,
  'Phishing' AS category,
  'Phishing emails try to trick you into revealing personal information. Learn to spot the red flags before it is too late.' AS summary,
  '<h3>What is Phishing?</h3><p>Phishing is a type of social engineering attack where cyber criminals disguise themselves as trustworthy entities via email, SMS, or fake websites to steal your login credentials, credit card details, or personal data.</p><h3>Red Flags to Watch For</h3><ul><li><strong>Urgent or threatening language</strong> – "Your account will be suspended in 24 hours!"</li><li><strong>Suspicious sender address</strong> – The domain does not match the organisation it claims to be from.</li><li><strong>Generic greetings</strong> – "Dear Customer" instead of your actual name.</li><li><strong>Unexpected attachments or links</strong> – Hover over links before clicking to verify the destination URL.</li><li><strong>Too-good-to-be-true offers</strong> – Lottery wins, unclaimed inheritance, or free prizes.</li></ul><h3>What to Do If You Receive a Phishing Email</h3><ol><li>Do NOT click any links or download attachments.</li><li>Report the email to your email provider as spam or phishing.</li><li>Report it to your organisation''s IT team if applicable.</li><li>File a complaint on this portal if you have suffered financial loss or data theft.</li></ol><h3>Prevention Tips</h3><p>Enable two-factor authentication (2FA) on all accounts. Use a reputable email filter and keep your browser and antivirus software updated.</p>' AS content,
  'mail-alert' AS icon,
  1 AS author_id) AS tmp
WHERE NOT EXISTS (SELECT 1 FROM articles WHERE title='How to Recognise a Phishing Email');

INSERT INTO articles (title, category, summary, content, icon, author_id)
SELECT * FROM (SELECT
  'Creating and Managing Strong Passwords' AS title,
  'Password Security' AS category,
  'Weak passwords are the number one cause of account breaches. Learn how to create passwords that are both strong and memorable.' AS summary,
  '<h3>Why Passwords Matter</h3><p>Your password is the first line of defence for every online account. A weak or reused password can lead to identity theft, financial loss, and data breaches affecting thousands of people.</p><h3>What Makes a Password Strong?</h3><ul><li><strong>Length</strong> – At least 12 characters (16+ is ideal).</li><li><strong>Complexity</strong> – Mix of uppercase, lowercase, numbers, and symbols.</li><li><strong>Unpredictability</strong> – Avoid names, birthdays, or dictionary words.</li><li><strong>Uniqueness</strong> – Never reuse the same password across different sites.</li></ul><h3>Passphrase Technique</h3><p>A passphrase like <em>Coffee#River!Mountain9</em> is both long and memorable. String together unrelated words with numbers and symbols.</p><h3>Use a Password Manager</h3><p>Tools like Bitwarden, 1Password, or KeePass can generate and securely store unique passwords for every site, so you only need to remember one master password.</p><h3>Enable Two-Factor Authentication</h3><p>2FA adds a second verification step (SMS code, authenticator app, or hardware key) so that even if your password is stolen, attackers cannot log in.</p>' AS content,
  'lock-check' AS icon,
  1 AS author_id) AS tmp
WHERE NOT EXISTS (SELECT 1 FROM articles WHERE title='Creating and Managing Strong Passwords');

INSERT INTO articles (title, category, summary, content, icon, author_id)
SELECT * FROM (SELECT
  'Understanding Malware – Types and Prevention' AS title,
  'Malware' AS category,
  'Malware can silently steal your data, encrypt your files, or turn your computer into a bot. Understand the types and how to stay protected.' AS summary,
  '<h3>What is Malware?</h3><p>Malware (malicious software) is any program designed to harm, exploit, or otherwise compromise a computer system without the user''s consent.</p><h3>Common Types</h3><ul><li><strong>Viruses</strong> – Attach to legitimate programs and spread when those programs are executed.</li><li><strong>Trojans</strong> – Disguised as useful software but carry hidden malicious payloads.</li><li><strong>Ransomware</strong> – Encrypts your files and demands a ransom for the decryption key.</li><li><strong>Spyware</strong> – Silently monitors your activity and sends data to attackers.</li><li><strong>Adware</strong> – Bombards you with unwanted advertisements and may redirect your browser.</li><li><strong>Worms</strong> – Self-replicate and spread across networks without user interaction.</li><li><strong>Rootkits</strong> – Hide deep in the OS to evade detection and give persistent backdoor access.</li></ul><h3>How Malware Spreads</h3><p>Email attachments, malicious links, infected USB drives, pirated software, and unpatched vulnerabilities are the most common infection vectors.</p><h3>Prevention</h3><ol><li>Keep your operating system and all software up to date.</li><li>Use a reputable antivirus / antimalware solution.</li><li>Avoid downloading software from untrusted sources.</li><li>Do not plug in unknown USB devices.</li><li>Enable a firewall and configure it to block unnecessary inbound connections.</li></ol>' AS content,
  'bug' AS icon,
  1 AS author_id) AS tmp
WHERE NOT EXISTS (SELECT 1 FROM articles WHERE title='Understanding Malware – Types and Prevention');

INSERT INTO articles (title, category, summary, content, icon, author_id)
SELECT * FROM (SELECT
  'Online Scams – How to Spot and Avoid Them' AS title,
  'Online Scams' AS category,
  'From fake job offers to romance fraud, online scams cost victims billions each year. Learn the warning signs to protect yourself.' AS summary,
  '<h3>Common Online Scam Types</h3><ul><li><strong>Advance-fee fraud (419 scam)</strong> – A "prince" or "lottery" needs your help transferring money and promises a share of the fortune.</li><li><strong>Fake job offers</strong> – Work-from-home jobs that require you to pay for training kits or forward money.</li><li><strong>Romance scams</strong> – Fraudsters build a relationship online before requesting money for emergencies.</li><li><strong>Tech support scams</strong> – A pop-up claims your computer is infected and asks you to call a number.</li><li><strong>Impersonation scams</strong> – Criminals pose as government agencies, banks, or couriers demanding immediate payment.</li><li><strong>Investment fraud</strong> – High-return cryptocurrency or stock schemes designed to steal deposits.</li></ul><h3>Warning Signs</h3><ul><li>You are asked to pay via gift cards, wire transfer, or cryptocurrency.</li><li>Offers sound too good to be true.</li><li>The person creates urgency or uses emotional pressure.</li><li>They ask for personal or financial information early in the relationship.</li></ul><h3>If You Have Been Scammed</h3><ol><li>Stop all contact with the scammer immediately.</li><li>Alert your bank if money has been transferred.</li><li>File a complaint on this portal with as much evidence as possible.</li><li>Report to your national cybercrime authority.</li></ol>' AS content,
  'alert-circle' AS icon,
  1 AS author_id) AS tmp
WHERE NOT EXISTS (SELECT 1 FROM articles WHERE title='Online Scams – How to Spot and Avoid Them');

INSERT INTO articles (title, category, summary, content, icon, author_id)
SELECT * FROM (SELECT
  'Cyberbullying – Recognise, Respond, Report' AS title,
  'Cyberbullying' AS category,
  'Cyberbullying causes serious psychological harm. Know your rights, what to document, and how to seek help.' AS summary,
  '<h3>What is Cyberbullying?</h3><p>Cyberbullying is the use of digital technology – social media, messaging apps, gaming platforms, or email – to repeatedly harass, intimidate, threaten, or humiliate an individual.</p><h3>Forms of Cyberbullying</h3><ul><li>Sending threatening or abusive messages.</li><li>Posting embarrassing photos or videos without consent.</li><li>Spreading false rumours online.</li><li>Impersonating someone to damage their reputation.</li><li>Deliberately excluding someone from online groups.</li><li>Doxxing – sharing someone''s private information publicly.</li></ul><h3>How to Respond</h3><ol><li><strong>Do not engage</strong> – Responding often escalates the situation.</li><li><strong>Document everything</strong> – Take screenshots with timestamps.</li><li><strong>Block and report</strong> – Use the platform''s built-in reporting tools.</li><li><strong>Tell a trusted adult</strong> – Parents, school counsellors, or employers.</li><li><strong>File a complaint</strong> – Use this portal or contact law enforcement if threats are involved.</li></ol><h3>Support Resources</h3><p>Reach out to a mental health professional if cyberbullying is affecting your wellbeing. You are not alone, and help is available.</p>' AS content,
  'users-x' AS icon,
  1 AS author_id) AS tmp
WHERE NOT EXISTS (SELECT 1 FROM articles WHERE title='Cyberbullying – Recognise, Respond, Report');

INSERT INTO articles (title, category, summary, content, icon, author_id)
SELECT * FROM (SELECT
  'Identity Theft – Protect Your Digital Identity' AS title,
  'Identity Theft' AS category,
  'Identity theft can ruin your finances and reputation. Learn what it is, how thieves get your data, and how to defend yourself.' AS summary,
  '<h3>What is Identity Theft?</h3><p>Identity theft occurs when someone uses your personal information – name, ID number, bank details, or social security number – without your permission, usually for financial gain.</p><h3>How Thieves Steal Your Identity</h3><ul><li>Data breaches at companies you have accounts with.</li><li>Phishing emails or fake websites.</li><li>Physical mail theft or dumpster diving for financial documents.</li><li>Shoulder surfing in public places.</li><li>Social media oversharing (birthdate, hometown, pet names used as passwords).</li><li>Skimming devices on ATMs or payment terminals.</li></ul><h3>Warning Signs</h3><ul><li>Unexpected bills or debt collection calls for accounts you did not open.</li><li>Unfamiliar transactions on your bank or credit card statements.</li><li>Denial of credit applications despite a good credit history.</li><li>Missing expected mail or emails.</li></ul><h3>Steps to Take If Your Identity Has Been Stolen</h3><ol><li>Alert your bank and credit card companies immediately.</li><li>Change passwords and enable 2FA on all affected accounts.</li><li>File a complaint on this portal with full details.</li><li>Contact your national identity fraud helpline.</li><li>Monitor your credit report for several months following the incident.</li></ol>' AS content,
  'fingerprint' AS icon,
  1 AS author_id) AS tmp
WHERE NOT EXISTS (SELECT 1 FROM articles WHERE title='Identity Theft – Protect Your Digital Identity');
