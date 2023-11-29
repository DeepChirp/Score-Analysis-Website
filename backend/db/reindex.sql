DROP INDEX idx_student_id ON scores;
DROP INDEX idx_exam_id ON scores;
DROP INDEX idx_class ON students;
DROP INDEX idx_student_id_exam_id ON scores;

CREATE INDEX idx_student_id ON scores (student_id);
CREATE INDEX idx_exam_id ON scores (exam_id);
CREATE INDEX idx_class ON students (class);
CREATE INDEX idx_student_id_exam_id ON scores (student_id, exam_id);