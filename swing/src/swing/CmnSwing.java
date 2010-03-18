package swing;

import model.CmnModel;

/**
 *
 * @author konne
 */
public class CmnSwing {
    public static void main(String args[]) {
        final CmnModel model = new CmnModel();

        java.awt.EventQueue.invokeLater(new Runnable() {
            public void run() {
                new CmnSwingFrame(model).setVisible(true);
            }
        });
    }
}
