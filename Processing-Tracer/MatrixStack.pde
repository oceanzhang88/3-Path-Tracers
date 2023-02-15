public enum MatType {
  SCALE, ROTATE, TRANSLATE, IDENTITY, TRANSPOSE
}

class Matrix {
  private float[][] m;
  private MatType type;
  
  Matrix(float[][] m, MatType type) {
    this.m = m;
    this.type = type;
  }
  
  public Point mult(Point p) {
    float x = m[0][0] * p.x + m[0][1] * p.y + m[0][2] * p.z + m[0][3] * 1;
    float y = m[1][0] * p.x + m[1][1] * p.y + m[1][2] * p.z + m[1][3] * 1;
    float z = m[2][0] * p.x + m[2][1] * p.y + m[2][2] * p.z + m[2][3] * 1;
    return new Point(x, y, z);
  }
  
  public PVector mult(PVector v) {
    float x = m[0][0] * v.x + m[0][1] * v.y + m[0][2] * v.z;
    float y = m[1][0] * v.x + m[1][1] * v.y + m[1][2] * v.z;
    float z = m[2][0] * v.x + m[2][1] * v.y + m[2][2] * v.z;
    return new PVector(x, y, z);
  }
}

class MatrixStack {
  private ArrayList<ArrayList<Matrix>> matrixStack;
  
  MatrixStack() {
    matrixStack = new ArrayList<ArrayList<Matrix>>();
    ArrayList layer = new ArrayList<Matrix>();
    layer.add(identityMT());
    matrixStack.add(layer);
  }
  
  public void pushLayer() {
    ArrayList cur = matrixStack.get(matrixStack.size() - 1);
    ArrayList layer = new ArrayList<Matrix>(cur);
    matrixStack.add(layer);
  }
  
  public void addToLayer(Matrix mt) {
    ArrayList cur = matrixStack.get(matrixStack.size() - 1);
    cur.add(mt);
  }
  
  public ArrayList<Matrix> popLayer() {
    if (!matrixStack.isEmpty()) {
      return matrixStack.remove(matrixStack.size() - 1);
    }
    return null;
  }
  
  public ArrayList<Matrix> peek() {
    return matrixStack.get(matrixStack.size() - 1);
  }
  
  public Point transform(Point v) {
    ArrayList<Matrix> curlayer = peek();
    Point vt = v;
    for (int i = curlayer.size() - 1; i >= 0; i--) {
      Matrix m = curlayer.get(i);
      vt = m.mult(vt);
    }
    return vt;
  }
  
  public PVector transform(PVector v) {
    ArrayList<Matrix> curlayer = peek();
    PVector vt = v;
    for (int i = curlayer.size() - 1; i >= 0; i--) {
      Matrix m = curlayer.get(i);
      vt = m.mult(vt);
    }
    return vt;
  }
}

Matrix translateMT(float x, float y, float z) {
  float[][] mat = new float[4][4];
  mat[0][0] = 1;
  mat[1][1] = 1;
  mat[2][2] = 1;
  mat[3][3] = 1;
  
  mat[0][3] = x;
  mat[1][3] = y;
  mat[2][3] = z;
  
  return new Matrix(mat, MatType.TRANSLATE);
}

Matrix scaleMT(float x, float y, float z) {
  float[][] mat = new float[4][4];
  mat[0][0] = x;
  mat[1][1] = y;
  mat[2][2] = z;
  mat[3][3] = 1;
  return new Matrix(mat, MatType.SCALE);
}

Matrix rotateXMT(float theta) {
  float[][] mat = new float[4][4];
  double radian = Math.toRadians(theta);
  mat[0][0] = 1;
  mat[1][1] = (float)Math.cos(radian);
  mat[2][2] = (float)Math.cos(radian);
  mat[2][1] = (float)Math.sin(radian);
  mat[1][2] = (float)-Math.sin(radian);
  mat[3][3] = 1;
  return new Matrix(mat, MatType.ROTATE);
}

Matrix rotateZMT(float theta) {
  float[][] mat = new float[4][4];
  double radian = Math.toRadians(theta);
  mat[0][0] = (float)Math.cos(radian);
  mat[1][1] = (float)Math.cos(radian);
  mat[2][2] = 1;
  mat[1][0] = (float)Math.sin(radian);
  mat[0][1] = (float)-Math.sin(radian);
  mat[3][3] = 1;
  return new Matrix(mat, MatType.ROTATE);
}

Matrix rotateYMT(float theta) {
  float[][] mat = new float[4][4];
  double radian = Math.toRadians(theta);
  mat[0][0] = (float)Math.cos(radian);
  mat[1][1] = 1;
  mat[2][2] = (float)Math.cos(radian);
  mat[2][0] = (float)-Math.sin(radian);
  mat[0][2] = (float)Math.sin(radian);
  mat[3][3] = 1;
  return new Matrix(mat, MatType.ROTATE);
}

Matrix identityMT() {
  float[][] mat = new float[4][4];
  mat[0][0] = 1;
  mat[1][1] = 1;
  mat[2][2] = 1;
  mat[3][3] = 1;
  return new Matrix(mat, MatType.IDENTITY);
}

Matrix rotateMTInv(Matrix mat) {
  Matrix inv = transposeMT(mat);
  inv.type = MatType.ROTATE;
  return inv;
}

Matrix transposeMT(Matrix mat) {
  float[][] matInv = new float[4][4];
  for (int i = 0; i < 4; i++) {
    for (int j = 0; j < 4; j++) {
      matInv[j][i] = mat.m[i][j];
    }
  }
  return new Matrix(matInv, MatType.TRANSPOSE);
}

Matrix translateMTInv(Matrix mat) {
  float[][] matInv = new float[4][4];
  matInv[0][0] = 1;
  matInv[1][1] = 1;
  matInv[2][2] = 1;
  matInv[3][3] = 1;
  
  matInv[0][3] = -mat.m[0][3];
  matInv[1][3] = -mat.m[1][3];
  matInv[2][3] = -mat.m[2][3];
  return new Matrix(matInv, MatType.TRANSLATE);
}

Matrix scaleMTInv(Matrix mat) {
  float[][] matInv = new float[4][4];
  matInv[0][0] = 1/mat.m[0][0];
  matInv[1][1] = 1/mat.m[1][1];
  matInv[2][2] = 1/mat.m[2][2];
  matInv[3][3] = mat.m[3][3];
  return new Matrix(matInv, MatType.SCALE);
}
