DROP INDEX idx_student_id ON scores;
DROP INDEX idx_exam_id ON scores;
DROP INDEX idx_class ON students;
DROP INDEX idx_student_id_exam_id ON scores;
DROP INDEX idx_subject_id ON scores;
DROP INDEX idx_exam_id_subject_id ON scores;
DROP INDEX idx_value ON scores;

CREATE INDEX idx_student_id ON scores (student_id);
CREATE INDEX idx_exam_id ON scores (exam_id);
CREATE INDEX idx_class ON students (class);
CREATE INDEX idx_student_id_exam_id ON scores (student_id, exam_id);
CREATE INDEX idx_subject_id ON scores (subject_id);
CREATE INDEX idx_exam_id_subject_id ON scores (exam_id, subject_id);
CREATE INDEX idx_value ON scores (value);