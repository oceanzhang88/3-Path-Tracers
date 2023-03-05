import java.util.Comparator;
import java.util.Collections;
import java.util.Arrays;
import java.util.List;

float epsilon = 0.00001f;
int recDepth = 10;

Color black = new Color(0, 0, 0);

List<String> WOList = Arrays.asList("lucy_100k.cli", "dragon_100k.cli", "buddha_100k.cli");

public enum WindingOrder {
  CW, CCW;
}
Color colorBlend(Color rgba, Color rgba2) {
  return new Color(rgba.r * rgba2.r, rgba.g * rgba2.g, rgba.b * rgba2.b);
}

Color colorMul(Color rgb, float factor) {
  Color out = new Color(rgb.r * factor, rgb.g * factor, rgb.b * factor);
  return out;
}

Color colorAdd(Color rgba, Color rgba2) {
  return new Color(rgba.r + rgba2.r, rgba.g + rgba2.g, rgba.b + rgba2.b);
}

color color2Color(Color c) {
  return color(c.r * 255, c.g * 255, c.b * 255, 255);
}

Color color2Color(color argb) {
  int a = (argb >> 24) & 0xFF;
  int r = (argb >> 16) & 0xFF;  // Faster way of getting red(argb)
  int g = (argb >> 8) & 0xFF;   // Faster way of getting green(argb)
  int b = argb & 0xFF;          // Faster way of getting blue(argb)
 return new Color(r, g, b);
}

int lightID = 1;
int objectID = 1;

Comparator<Triangle> tricmpX = (Triangle t1, Triangle t2) -> Float.compare(t1.centroid().x, t2.centroid().x);
Comparator<Triangle> tricmpY = (Triangle t1, Triangle t2) -> Float.compare(t1.centroid().x, t2.centroid().x);
Comparator<Triangle> tricmpZ = (Triangle t1, Triangle t2) -> Float.compare(t1.centroid().x, t2.centroid().x);


int timer;  // global variable

void reset_timer()
{
  timer = millis();
}

void print_timer()
{
  int new_timer = millis();
  int diff = new_timer - timer;
  float seconds = diff / 1000.0;
  println ("timer = " + seconds);
}

HitTest getHitTest(SceneObject object) {
    HitTest ht = null;
    if (object instanceof Triangle) {
      ht = (Triangle)object;
    } else if (object instanceof BBox) {
      ht = (BBox)object;
    } else if (object instanceof BVH) {
      ht = (BVH)object;
    } else if (object instanceof Instance) {
      ht = (Instance)object;
    } else if (object instanceof Sphere) {
      ht = (Sphere)object;
    } else {
      println("Unkown scene object type!");
    }
    return ht;
  }
